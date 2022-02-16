#!/bin/bash

# this is a utility script for running the docker-compose file on AWS

# I had trouble getting the docker-compose.yml from the linuxserver/wireguard
# GitHub README to run both on MacOS and on AmazonLinux2 on an AWS Lightsail
# instance. The trouble was: the wireguard image actually needs you to mount
# a piece of the linux operating system called the "Linux Headers" into the
# container. Each OS has it's own headers. Note, these are literally C .h
# files for a given LinuxOS.

# I found the solution on this GitHub issue:
# https://github.com/linuxserver/docker-wireguard/issues/84

# Basically, this wireguard image has helper features when run on Ubuntu
# to automatically download the Linux Kernel headers. But if you're not
# running the docker container on a UbuntuOS host, you need to install
# the Linux headers for the host manually.

# Install the AmazonLinux2 Headers to /usr/src
yum install -y kernel-headers-$(uname -r) kernel-devel-$(uname -r)

EC2_PUBLIC_IP=$(curl http://169.254.169.254/latest/meta-data/public-ipv4) \
    docker-compose up
