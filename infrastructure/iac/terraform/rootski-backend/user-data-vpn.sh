#!/bin/bash -xe

# act as the super user for this script
sudo su

# log output of this script to console
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

# update and install docker
# NOTE, -y makes yum answer yes to all prompts
# httpd-tools is for bcrypt via the htpasswd command for generating basic auth passwords for the /docs and traefik UIs
yum update -y
yum -y install docker git python38 python38-pip httpd-tools
usermod -a -G docker ec2-user # allow ec2-user to use docker commands

# install git-lfs (for the initial data CSV files to seed the database)
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash
yum install -y git-lfs

# install docker-compose and make the binary executable
curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# start docker
service docker start

# mount the network file system where the rootski files are kept
yum install -y amazon-efs-utils
# create the /root directory if it doesn't exist
[[ -d /root ]] || mkdir /root
cd /
mount -t efs "${ROOTSKI_FILE_SYSTEM_ID}":/ efs/ || echo "File system is already mounted";

# fetch the rootski private Bitbucket "access" AKA read-only SSH private key
python3 -m pip install xonsh
python3 -m xonsh -c '
from pathlib import Path
Path("/home/ec2-user/.ssh/").mkdir(parents=True, exist_ok=True)
ssm_response = $(aws ssm get-parameter \
    --name /rootski/ssh/private-key \
    --with-decryption \
    --region us-west-2)
import json
rootski_private_key = json.loads(ssm_response)["Parameter"]["Value"]
echo @(rootski_private_key) > /home/ec2-user/.ssh/rootski.id_rsa
chmod 600 /home/ec2-user/.ssh/rootski.id_rsa
'

# add bitbucket.org to known_hosts
ssh-keyscan -t rsa -H bitbucket.org | tail -n +1 > /home/ec2-user/.ssh/known_hosts

# set the ssh config for bitbucket.org
cat <<EOF > /home/ec2-user/.ssh/config
Host bitbucket.org
    HostName bitbucket.org
    User git
    StrictHostKeyChecking no
    UserKnownHostsFile /home/ec2-user/.ssh/known_hosts
    IdentityFile /home/ec2-user/.ssh/rootski.id_rsa
EOF

# clone the rootski repository if it isn't already present
cd /root
[[ -d /home/ec2-user/rootski ]] \
    || GIT_SSH_COMMAND='ssh -F /home/ec2-user/.ssh/config' \
    git clone git@bitbucket.org:eriddoch1/rootski.git

# pull the latest code from the rootski repo
cd /home/ec2-user/rootski
git remote set-url origin git@bitbucket.org:eriddoch1/rootski.git # make sure we pull over ssh
git stash
GIT_SSH_COMMAND='ssh -F /home/ec2-user/.ssh/config' \
    git pull origin

# replace the public ip of this instance in parameter store
EC2_PUBLIC_IP=$(curl http://169.254.169.254/latest/meta-data/public-ipv4)
# SSM_PARAM_NAME="/ROOTSKI/BACKEND/public-ip"
# aws ssm put-parameter \
#     --name "$SSM_PARAM_NAME" \
#     --type "String" \
#     --description "Last known IP address of the rootski webserver backend" \
#     --value "$EC2_PUBLIC_IP" \
#     --region "${AWS_REGION}" \
#     --overwrite

# create and apply the change set
aws cloudformation create-change-set \
    --stack-name "Rootski-Subdomain-CF" \
    --change-set-name "update-backend-ip" \
    --change-set-type "UPDATE" \
    --use-previous-template \
    --parameters \
        ParameterKey="EC2PublicIp",ParameterValue="$EC2_PUBLIC_IP" \
        ParameterKey="RootskiFrontEndStackName",ParameterValue="Rootski-Front-End-CF" \
    --region "${AWS_REGION}"

# buy some time for traefik/lets encrypt by waiting for the change set to finish creating
aws cloudformation wait change-set-create-complete \
    --stack-name "Rootski-Subdomain-CF" \
    --change-set-name "update-backend-ip" \
    --region "${AWS_REGION}"

# try to update the ip address (change set)
aws cloudformation execute-change-set \
    --change-set-name "update-backend-ip" \
    --stack-name "Rootski-Subdomain-CF" \
    --region "${AWS_REGION}"

# deploy docker stack
make start-backend

# /usr/local/bin/docker-compose build
# /usr/local/bin/docker-compose up

# run this command to unmount the file system before shutting off the instance
# cd ~ && umount efs # not a typo: command is umount


# def view_user_data_log():
#     cat /var/log/user-data.log
