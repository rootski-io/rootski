#!/bin/bash

sudo su

# update and install docker
# NOTE, -y makes yum answer yes to all prompts
# httpd-tools is for bcrypt via the htpasswd command for generating basic auth passwords for the /docs and traefik UIs
yum update -y
yum -y install docker git python38 python38-pip httpd-tools zsh
usermod -a -G docker ec2-user # allow ec2-user to use docker commands

# install git-lfs (for the initial data CSV files to seed the database)
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash
yum install -y git-lfs

# start docker
service docker start

# install docker-compose and make the binary executable
curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# install ohmyzsh
sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"

# configure ohmyzsh
cat << EOF >> /home/ec2-user/.zshrc
ZSH_THEME="bira"
plugins=(git python pip docker docker-compose web-search zsh-autosuggestions zsh-syntax-highlighting vi-mode python pip docker docker-compose web-search zsh-autosuggestions zsh-syntax-highlighting vi-mode)
source \$ZSH/oh-my-zsh.sh

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

PATH="\$PATH:/usr/local/bin"
EOF


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

# clone rootski
cd /home/ec2-user
GIT_SSH_COMMAND='ssh -F /home/ec2-user/.ssh/config' \
    git clone git@bitbucket.org:eriddoch1/rootski.git
