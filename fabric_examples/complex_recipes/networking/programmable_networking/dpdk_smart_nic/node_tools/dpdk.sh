#!/bin/bash
MESON=`which meson`
NINJA=`which ninja`
export PATH=$PATH:$MESON:$NINJA
wget https://fast.dpdk.org/rel/dpdk-23.07.tar.xz
tar -xJvf dpdk-23.07.tar.xz
cd dpdk-23.07
meson setup build
cd build
ninja
sudo meson install
sudo ldconfig
meson configure -Dexamples=all
ninja