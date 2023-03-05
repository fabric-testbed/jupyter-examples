#!/bin/bash

image=$1
username=$2

script_dir="$(cd "$(dirname "$0")" && pwd)"

if ping6 -c 1 google.com &> /dev/null; then
    man_ip_type=ipv6
else
    man_ip_type=ipv4
fi




if [[ $image == "default_rocky_8" ]]; then
    sudo dnf install -y epel-release 
    sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo 
    sudo dnf install -y docker-ce docker-ce-cli containerd.io 
    sudo mkdir -p /etc/docker 
    sudo cp ${script_dir}/docker/daemon_${man_ip_type}.json /etc/docker/daemon.json 
    sudo systemctl start docker 
    sudo usermod -aG docker $username
    sudo dnf install -y https://repos.fedorapeople.org/repos/openstack/openstack-yoga/rdo-release-yoga-1.el8.noarch.rpm
    sudo dnf install -y openvswitch libibverbs tcpdump net-tools python3.9 vim iftop
    pip3.9 install docker rpyc --user 
    sudo systemctl enable --now openvswitch 
    sudo sysctl --system 
else
    echo invalid image type $image  
fi