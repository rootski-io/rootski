#!/bin/bash -xe

# act as the super user for this script
sudo su

# log output of this script to console
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

# map python -> python2 (yum needs python2)
unlink /usr/bin/python
ln -sfn /usr/bin/python2 /usr/bin/python

# update and install docker
# NOTE, -y makes yum answer yes to all prompts
# httpd-tools is for bcrypt via the htpasswd command for generating basic auth passwords for the /docs and traefik UIs
yum update -y
yum -y install docker git httpd-tools zsh
usermod -a -G docker ec2-user # allow ec2-user to use docker commands

# install ohmyzsh
sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -) --unattended"

# configure ohmyzsh
cat << EOF > /home/ec2-user/.zshrc
ZSH_THEME="bira"
plugins=(git python pip docker docker-compose web-search zsh-autosuggestions zsh-syntax-highlighting vi-mode python pip docker docker-compose web-search zsh-autosuggestions zsh-syntax-highlighting vi-mode)
source \$HOME/.oh-my-zsh/oh-my-zsh.sh

# ERICs changes
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

function c() {
    pygmentize -g \$@ || cat \$@
}

# these are commented out until I can figure out how to install exa on amazon linux
# alias ls="exa --icons"
# alias lsa="exa -lah --git --group --octal-permissions --color-scale --group-directories-first"
alias drm='docker container rm --force \$(docker ps -aq)'

# enable vi mode
bindkey -v
EOF
rm -f /root/.zshrc || echo "/root/.zshrc does not exist"
cp /home/ec2-user/.zshrc /root/

# install git-lfs (for the initial data CSV files to seed the database)
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash
yum install -y git-lfs

# install docker-compose and make the binary executable
curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose

# start docker
service docker start

# mount the network file system where the rootski files are kept
yum install -y amazon-efs-utils
# create the /efs directory if it doesn't exist
[[ -d /efs ]] || mkdir /efs
cd /efs

# TODO - decide if we *do* want to mount the efs volume
# mount -t efs "${ROOTSKI_FILE_SYSTEM_ID}":/ efs/ || echo "File system is already mounted";
# mount -t efs "fs-97ec6392":/ efs/ || echo "File system is already mounted";

# map python -> python3.7 (so that the makefile works; BUT this breaks yum)
unlink /usr/bin/python
ln -sfn /usr/bin/python3.7 /usr/bin/python
python -m venv venv/
source ./venv/bin/activate

# fetch the rootski private Bitbucket "access" AKA read-only SSH private key
python -m pip install xonsh
python -m xonsh -c '
from pathlib import Path
import json

Path("/efs/.ssh/").mkdir(parents=True, exist_ok=True)
ssm_response = $(aws ssm get-parameter \
    --name /rootski/ssh/private-key \
    --with-decryption \
    --region us-west-2)
rootski_private_key = json.loads(ssm_response)["Parameter"]["Value"]
echo @(rootski_private_key) > /efs/.ssh/rootski.id_rsa
chmod 600 /efs/.ssh/rootski.id_rsa
'

# add bitbucket.org to known_hosts
ssh-keyscan -t rsa -H bitbucket.org | tail -n +1 > /efs/.ssh/known_hosts

# set the ssh config for bitbucket.org
cat <<EOF > /efs/.ssh/config
Host bitbucket.org
    HostName bitbucket.org
    User git
    StrictHostKeyChecking no
    UserKnownHostsFile /efs/.ssh/known_hosts
    IdentityFile /efs/.ssh/rootski.id_rsa
EOF

# clone the rootski repository if it isn't already present
cd /efs
[[ -d /efs/rootski ]] \
    || GIT_SSH_COMMAND='ssh -F /efs/.ssh/config' \
    git clone git@bitbucket.org:eriddoch1/rootski.git

# pull the latest code from the rootski repo
cd /efs/rootski
git remote set-url origin git@bitbucket.org:eriddoch1/rootski.git # make sure we pull over ssh
git stash
GIT_SSH_COMMAND='ssh -F /efs/.ssh/config' \
    git pull origin

# pull the larger CSV files to seed the database; TODO - remove this in favor of restoring from S3 backup
GIT_SSH_COMMAND='ssh -F /efs/.ssh/config' \
    git lfs pull

# point traefik.rootski.io and api.rootski.io at this instance's public IP
python -m xonsh -c '
from uuid import uuid4

STACK_NAME_TEMPLATE: str = "Rootski-{subdomain}-Subdomain-CF"
EC2_PUBLIC_IP: str = $(curl http://169.254.169.254/latest/meta-data/public-ipv4)
EC2_AVAIL_ZONE = $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
AWS_REGION = EC2_AVAIL_ZONE.strip("abc") # parse the region from the AZ like us-west-1a

def generate_change_set_name():
   # Change Set names have to be unique. They accumulate on the CF Stack in AWS.
   return "update-subdomain-ip-" + str(uuid4())[:5]

def update_dns_record(subdomain, ip):
    stack_name: str = STACK_NAME_TEMPLATE.format(subdomain=subdomain)
    print(f"[rootski] updating stack {stack_name} with subdomain {subdomain} and ip {ip}")
    change_set_name = generate_change_set_name()

    # create and apply the change set
    aws cloudformation create-change-set \
        --stack-name @(stack_name) \
        --change-set-name @(change_set_name) \
        --change-set-type "UPDATE" \
        --use-previous-template \
        --parameters \
            ParameterKey="PublicIP",ParameterValue=@(ip) \
            ParameterKey="Subdomain",ParameterValue=@(subdomain) \
            ParameterKey="RootskiFrontEndStackName",ParameterValue="Rootski-Front-End-CF" \
        --region @(AWS_REGION)

    # buy some time for traefik/lets encrypt by waiting for the change set to finish creating
    aws cloudformation wait change-set-create-complete \
        --stack-name @(stack_name) \
        --change-set-name @(change_set_name) \
        --region @(AWS_REGION)

    # try to update the ip address (change set)
    aws cloudformation execute-change-set \
        --change-set-name @(change_set_name) \
        --stack-name @(stack_name) \
        --region @(AWS_REGION)

update_dns_record("api", EC2_PUBLIC_IP)
update_dns_record("traefik", EC2_PUBLIC_IP)
'

# deploy docker stack
make install
make build-images
make start-backend-prod
make await-db-healthy
make seed-prod-db

# run this command to unmount the file system before shutting off the instance
# cd ~ && umount efs # not a typo: command is umount
