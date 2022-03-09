#!/bin/bash -xe

set -x

# # act as the super user for this script
sudo su

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

# configure AWS credentials
mkdir -p /home/ec2-user/.aws
cat << EOF > /home/ec2-user/.aws/credentials
[rootski]
aws_access_key_id={{ AWS_ACCESS_KEY_ID }}
aws_secret_access_key={{ AWS_SECRET_ACCESS_KEY }}
region=us-west-2

[default]
aws_access_key_id={{ AWS_ACCESS_KEY_ID }}
aws_secret_access_key={{ AWS_SECRET_ACCESS_KEY }}
region=us-west-2
EOF
cp -r /home/ec2-user/.aws /root/

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
# rm -f /root/.zshrc || echo "/root/.zshrc does not exist"
cp /home/ec2-user/.zshrc /root/

# install docker-compose and make the binary executable
curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/bin/docker-compose
chmod +x /usr/bin/docker-compose

# start docker
service docker start

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
import os
os.environ["AWS_CONFIG_FILE"] = "/home/ec2-user/.aws/credentials"
os.environ["AWS_PROFILE"] = "rootski"
$AWS_CONFIG_FILE = "/home/ec2-user/.aws/credentials"

Path("/home/ec2-user/.ssh/").mkdir(parents=True, exist_ok=True)
ssm_response = $(aws ssm get-parameter \
    --name /rootski/ssh/private-key \
    --with-decryption \
    --region us-west-2 \
    --profile rootski)
rootski_private_key = json.loads(ssm_response)["Parameter"]["Value"]
echo @(rootski_private_key) > /home/ec2-user/.ssh/rootski.id_rsa
chmod 600 /home/ec2-user/.ssh/rootski.id_rsa
'

# add github.com to known_hosts
ssh-keyscan -t rsa -H github.com | tail -n +1 > /home/ec2-user/.ssh/known_hosts

# set the ssh config for github.com
cat << EOF > /home/ec2-user/.ssh/config
Host github.com
    HostName github.com
    User git
    StrictHostKeyChecking no
    UserKnownHostsFile /home/ec2-user/.ssh/known_hosts
    IdentityFile /home/ec2-user/.ssh/rootski.id_rsa
EOF

# clone the rootski repository if it isn't already present
cd /home/ec2-user
[[ -d /home/ec2-user/rootski ]] \
    || GIT_SSH_COMMAND='ssh -F /home/ec2-user/.ssh/config' \
    git clone --depth 1 git@github.com:rootski-io/rootski.git

# deploy docker stack
cd rootski

# create directories that are mounted as volumes in the docker
# containers but aren't in github
sudo mkdir infrastructure/containers/postgres/data
sudo mkdir infrastructure/containers/postgres/backups

# install necessary dependencies
make install-lightsail

# builds the docker images for the postgres and database-backup contaienrs
make build-images

# runs the postgres and database-backup containers in a swarm
make start-database-stack

# waits until the database is initialized and restores the database from
# the most recent S3 backup
make restore-database-from-most-recent-s3-backup

# sets the database to backup to S3 continually on an interval
make backup-database-to-s3-on-interval

# run this command to unmount the file system before shutting off the instance
# cd ~ && umount efs # not a typo: command is umount
