#!/bin/bash
MESON=`which meson`
NINJA=`which ninja`
export PATH=$PATH:$MESON:$NINJA
NAME=`cat /etc/os-release  | grep "^NAME="`

if [[ $NAME == *Rocky* ]]; then
    export PKG_CONFIG_PATH=/usr/local/lib64/pkgconfig 
    git clone https://github.com/pktgen/Pktgen-DPDK.git
    cd Pktgen-DPDK 
    make
else
    git clone http://dpdk.org/git/apps/pktgen-dpdk
    cd pktgen-dpdk
    make
fi