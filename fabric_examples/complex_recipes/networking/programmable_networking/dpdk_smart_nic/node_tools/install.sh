#!/bin/bash
NAME=`cat /etc/os-release  | grep "^NAME="`

if [[ $NAME == *Rocky* ]]; then
    # Rocky
    sudo dnf install -y net-tools pciutils  python3.9 numactl-devel wget libpcap createrepo perl
    sudo dnf groupinstall -y "Development Tools"
    sudo dnf install -y tcl lsof gcc-gfortran kernel-modules-extra tk
    sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
            && python3 get-pip.py \
            && rm -rf get-pip.py
    sudo python3 -m pip install --no-cache-dir meson ninja pyelftools
    wget https://rpmfind.net/linux/centos-stream/9-stream/CRB/x86_64/os/Packages/libpcap-devel-1.10.0-4.el9.x86_64.rpm
    sudo rpm -ivh libpcap-devel-1.10.0-4.el9.x86_64.rpm
    sudo sed -i '/^Defaults[[:space:]]*secure_path/ s/$/:\/usr\/local\/bin/' /etc/sudoers
else
    # Ubuntu
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt install python3.9 -y
    sudo apt install -y build-essential net-tools pciutils libnuma-dev wget pkg-config libpcap-dev
    sudo curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
            && python3 get-pip.py \
            && rm -rf get-pip.py
    sudo python3 -m pip install --no-cache-dir meson ninja pyelftools
    #sudo sed -i '/^Defaults[[:space:]]*secure_path/ s/$/:\/usr\/local\/bin/' /etc/sudoers    
fi

