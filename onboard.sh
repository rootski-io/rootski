#!/bin/bash

# tell bash to print each of the commands in this script as they are run (helps for debugging)
set -x

# NOTE: This script does require human intervention. You'll be prompted for your
# sudo password and other things.
#
# This script tries to do as much setup for rootski contributors as possible.
# It is designed to run on MacOS or Linux WSL2 (specifically Ubuntu or other debian distros)
#
# This script will attempt to install the following tools. If any of these fail to install
# using the script, you can just install each of these things manually. If your process
# can make this script better, we'd love to a PR to implement your fixes!

# - pyenv                             Tool for installing python and switching between python versions.
#                                     This RealPython video is a decent intro. I could see it being
#                                     confusing to total Linux/bash/python beginners.
#                                     https://www.youtube.com/watch?v=ikKpWM4_3g4
#                                     Their GitHub page has nice pictures, too :D
#                                     https://github.com/pyenv/pyenv

# - python 3.9.6 (using pyenv)        A recent version of python3; the script will try to make it so
#                                     that "pyenv shell 3.9.6" is run whenever you open your terminal
#                                     which should make the "python" command refer to python3.9.6
#                                     If this doesn't work, try to set up pyenv on your own. It's the #1
#                                     way to manage different python versions and installing python.
#                                     If you don't want to figure that out, just try to get python3.9.x
#                                     installed on your machine some other way and preferably make it so
#                                     that "python" refers to 3.9.6 (maybe via an alias).

# - git                               Tool for collaborating on our codebase / keeping track of changes

# - git-lfs                           Tool for including large files in a git repo without making

#                                     the size of the repo massive
# - homebrew (on Mac)                 Package manager for mac -- like "pip" but for ANY program :D

# - AWS CLI v2                        CLI tool for working with Amazon Web Services

# - Docker Desktop (on Mac), on       GUI and CLI Tool for running docker containers on your local machine;
#   Windows, you need this with       this makes it REALLY easy to run rootski locally and in production.
#   the WSL2; on Linux you just       ALERT: installing this is likely to fail in this script :(
#   need "docker"                     You can get it here:
#                                     https://www.docker.com/products/docker-desktop

# - Docker Compose                    CLI Tool for running multiple docker containers at once.

# - curl                              CLI Tool for making HTTP requests and downloading thigns.
#                                     Like "wget" if you know what that is.

# - sed                               CLI Tool for editing text files without human intervention.
#                                     It's used in this script to modify your ~/.bash_profile,
#                                     ~/.zshrc, or ~/.bashrc

# - z-shell via ohmyzsh (optional;    A very nice "shell framework" that brings color and joy
#   comment out if you don't want     to your terminal--also a lot of neat autocomplete features
#   this)                             so that pressing TAB can autocomplete a lot more commands.
#
#                                     If you already have Ohmyzsh, this will do nothing. But if
#                                     you already have some fancy terminal solution set up and you
#                                     don't want ohmyzsh, you can comment out the lines in the
#                                     script for these. OR comment it out if you don't want this
#                                     script to set your ZSH_THEME to "bira".

# - DBeaver                           Desktop app for connecting to SQL databases.
#                                     We use it to connect to the rootski PostgreSQL database.
#                                     This makes exploring the data a happier experience :D

# - a python virtual environment      If you don't know what a virtual environment is... LEARN :D
#                                     This is a super important tool for developing production
#                                     Python code. I recommend using "python -m venv" (not virtualenv).
#                                     This video seems decent (If I watch it and change my mind... I'll do something)
#                                     https://www.youtube.com/watch?v=MGTX5qI2Jts&ab_channel=anthonywritescode

# Requirements:
# - This script assumes you have Python3 available on your PATH at "python" or "python3".
#   I recommend installing "pyenv" to manage your python versions for you.
# - You need "sudo" on your system. You'll be asked for your password.

function set_script_vars() {
    # make sure all script commands are done relative to the rootski/ directory
    export THIS_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    cd "$THIS_DIR"
}
set_script_vars

########################
# --- Mac OS Setup --- #
########################

# install rootski dependencies for mac
which brew || echo "$OSTYPE" | grep 'darwin' && /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

# get the "brew upgrade" out of the way and disable it for the rest of the "brew install" commands
which brew || brew upgrade
export HOMEBREW_NO_AUTO_UPDATE=1

# install the rest of the rootski dependencies with brew
which brew && which make || brew install make || echo "mac: could not install make"
which brew && which zip || brew install zip || echo "mac: could not install zip/unzip"
which brew && which awk || brew install awk || echo "mac: could not install awk"
which brew && which aws || brew install awscli || echo "mac: could not install awscli"
which brew && which git || brew install git || echo "mac: could not install git"
which brew && which git-lfs || brew install git-lfs || echo "mac: could not install git failed"
which brew && which docker || brew install --cask docker || echo "mac: could not install docker-desktop"
which brew && which curl || brew install curl || echo "mac: could not install curl"
which brew && which sed || brew install sed || echo "mac: could not install sed"
which brew && which zsh || brew install zsh || echo "mac: could not install zsh"

# install OhMyZSH and configure it with some nice settings
which brew && [ -d ~/.oh-my-zsh ] || sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
which brew && sed -i "" 's/^ZSH_THEME=".\+"/ZSH_THEME=\"bira\"/g' "$HOME/.zshrc"
which brew && exec "$HOME/.zshrc"
# plugin: zsh-autosuggestions
which brew && git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
# plugin: zsh-syntax-highlighting
which brew && git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
# add these two plugins and enable some of the default ones
which brew && sed -i "" 's/\(^plugins=([^)]*\)/\1 python pip docker docker-compose web-search zsh-autosuggestions zsh-syntax-highlighting vi-mode/' "$HOME/.zshrc"
# set the ZSH_THEME to "bira"
which brew && sed -i "" 's/_THEME=\".*\"/_THEME=\"bira\"/g' "$HOME/.zshrc"

# make 'ls' more colorful by replacing it with 'exa'
which brew && brew install exa
which brew && which exa && echo "onboard.sh aliases:" >> "$HOME/.zshrc"
which brew && which exa && echo "alias ls='exa --icons'" >> "$HOME/.zshrc"
which brew && which exa && echo "alias lsa='exa -lah'" >> "$HOME/.zshrc"

# make 'cat' colorful (but with the 'c' command)
which brew && brew install pygments
which brew && cat << EOF >> "$HOME/.zshrc"

# onboard.sh alias:
# pass streams of text to pygmentize first, if pygmentize can guess what language
# is in the stream, it syntax highlights it. If if can't guess, it forwards the
# stream to 'cat' in uncolored form
function c() {
    pygmentize -g \$@ || cat \$@
}
EOF

#################################################
# --- Linux Setup (Ubuntu or debian distro) --- #
#################################################

# prepare apt-get to install several packages
which apt-get && apt-get update

# install rootski dependencies for linux (ubuntu or other deb based distros)
which apt-get && which zip || sudo apt-get install -y zip || echo "linux: could not install zip/unzip"
which apt-get && which awk || sudo apt-get install -y awk || echo "linux: could not install awk"
which apt-get && which curl || sudo apt-get install -y curl || echo "linux: could not install curl"

# install aws cli
which apt-get && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" || echo "linux: could not download awscli"
which apt-get && mkdir -p artifacts || echo "linux: could not create artifacts dir"
which apt-get && unzip awscliv2.zip -do artifacts || echo "linux: could not unzip awscliv2.zip"
which apt-get && sudo ./artifacts/aws/install || echo "not linux" || echo "linux: could not run awscli install script"

# install git
which apt-get && sudo apt-get install -y git

# install git-lfs
which apt-get && sudo apt-get install -y software-properties-common
which apt-get && sudo curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
which apt-get && sudo apt-get install -y git-lfs || echo "linux: could not install git-lfs"
which apt-get && which sed || sudo apt-get install -y sed || echo "linux: could not install sed"
which apt-get && which zsh || sudo apt-get install -y zsh || echo "linux: could not install zsh"

# install MANY linux dependencies for installing pyenv and python
which apt-get \
    && sudo apt-get install -y gcc make build-essential libssl-dev zlib1g-dev libbz2-dev \
        libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
        xz-utils tk-dev libffi-dev liblzma-dev python-openssl \
    || echo "linux: could not install pyenv dependencies"

# install OhMyZSH if it isn't already installed
which apt-get && [ -d ~/.oh-my-zsh ] || sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" \
# plugin: zsh-autosuggestions
which apt-get && git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
# plugin: zsh-syntax-highlighting
which apt-get && git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
# add these two plugins and enable some of the default ones
which apt-get && sed -i 's/\(^plugins=([^)]*\)/\1 python pip docker docker-compose web-search zsh-autosuggestions zsh-syntax-highlighting vi-mode/' "$HOME/.zshrc"
# set the ZSH_THEME to "bira"
which apt-get && sed -i 's/_THEME=\".*\"/_THEME=\"bira\"/g' "$HOME/.zshrc"

##########################################
# --- Final Setup for Both Platforms --- #
##########################################

# install pyenv if not present; also python 3.9.6
which pyenv || curl https://pyenv.run | $SHELL

# add pyenv lines to your shell startup script so that you are in python 3.9.6 by default;
# lines are only added if the string "pyenv init" doesn't appear anywhere in your startup script
for path in ~/.bash_profile ~/.zshrc ~/.bashrc; do
    cat "$path" | grep 'pyenv init' || cat << EOF >> "$path"
# begin rootski/onboard.sh changes

# pyenv
export PYENV_ROOT="\$HOME/.pyenv"
export PATH="\$PYENV_ROOT/bin:$PATH"
eval "\$(pyenv init --path)"
pyenv shell 3.9.6

# end rootski/onboard.sh changes
EOF
done

# install python 3.9.6
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
pyenv versions | grep "3.9.6" || pyenv install 3.9.6

# reset the shell to apply the changes in the start script; this should activate python 3.9.6
exec $SHELL
# reset the script vars since they were probably just wiped
set_script_vars

# create/activate a virtual environment for rootski; this should be a python 3.9.6 environment
[ -d "$THIS_DIR/venv" ] || rm -rf venv
python -m venv "$THIS_DIR/venv"
source "$THIS_DIR/venv/bin/activate"

# install xonsh into the venv so that we can use make.xsh
python -m pip install xonsh

# install docker-compose
python -m pip install docker-compose


# init git-lfs in your copy of this repo and pull the large data files
git lfs install
git lfs pull

# add [rootski] section to ~/.aws/credentials (you'll have to manually fill this out with your rootski credentials)
mkdir -p "$HOME/.aws"
cat "$HOME/.aws/credentials" | grep "rootski" || cat << EOF >> "$HOME/.aws/credentials"

# reach out to a Rootski admin to get AWS credentials; stick them here
# whenever you use the AWS CLI locally, use these credentials by adding "--profile rootski"
# to the command. For example: "aws s3 <args to upload something to s3> --profile rootski"
[rootski]
aws_access_key_id=<your rootski iam user access key>
aws_secret_access_key=<your rootski iam user secret access key>
region=us-west-2
EOF
