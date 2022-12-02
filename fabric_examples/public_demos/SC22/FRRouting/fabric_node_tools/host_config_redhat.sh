#!/bin/bash

# Install Packages
sudo sudo dnf install -y epel-release
sudo /usr/bin/crb enable
sudo dnf install -y vim httpd iproute-tc net-tools pciutils tcpdump iftop iperf3 

