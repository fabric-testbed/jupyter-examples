#!/bin/bash
NAME=`cat /etc/os-release  | grep "^NAME="`

if [[ $NAME == *Rocky* ]]; then
    sudo rpm -ivh /home/rocky/libpcap-devel-1.10.0-4.el9.x86_64.rpm
    sudo mount -o ro,loop /home/rocky/MLNX_OFED_LINUX-23.07-0.5.0.0-rhel9.2-x86_64.iso /mnt/
else
    sudo mount -o ro,loop /home/ubuntu/MLNX_OFED_LINUX-23.07-0.5.1.2-ubuntu20.04-x86_64.iso /mnt/
fi
sudo /mnt/mlnxofedinstall --force
sudo /etc/init.d/openibd restart
