#!/bin/bash

# Setup NAT64 based on https://nat64.net/
sudo sed -i '/nameserver/d' /etc/resolv.conf
sudo sh -c 'echo nameserver 2a00:1098:2c::1 >> /etc/resolv.conf' 
sudo sh -c 'echo nameserver 2a01:4f8:c2c:123f::1 >> /etc/resolv.conf' 
sudo sh -c 'echo nameserver 2a00:1098:2b::1 >> /etc/resolv.conf'

# install Docker compose and buildx plugins (does not require sudo - installs for this user only)

mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
curl -SL https://github.com/docker/buildx/releases/download/v0.11.2/buildx-v0.11.2.linux-amd64 -o ~/.docker/cli-plugins/docker-buildx
chmod +x ~/.docker/cli-plugins/docker-buildx 

# install any missing packages
sudo apt install tree