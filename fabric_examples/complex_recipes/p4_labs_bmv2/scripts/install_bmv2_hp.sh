#!/bin/bash

# Setup NAT64 based on https://nat64.net/
# sudo sed -i '/nameserver/d' /etc/resolv.conf
# sudo sh -c 'echo nameserver 2a00:1098:2c::1 >> /etc/resolv.conf' 
# sudo sh -c 'echo nameserver 2a01:4f8:c2c:123f::1 >> /etc/resolv.conf' 
# sudo sh -c 'echo nameserver 2a00:1098:2b::1 >> /etc/resolv.conf'

git clone https://github.com/p4lang/behavioral-model.git

sudo apt-get update && sudo apt-get install -y automake cmake libgmp-dev libpcap-dev libboost-dev libboost-test-dev libboost-program-options-dev libboost-system-dev libboost-filesystem-dev libboost-thread-dev libevent-dev libtool flex bison pkg-config g++ libssl-dev python3-pip automake cmake  libgmp-dev libpcap-dev libboost-dev libboost-test-dev libboost-program-options-dev libboost-system-dev  libboost-filesystem-dev libboost-thread-dev  libevent-dev libtool flex bison pkg-config g++ libssl-dev libffi-dev python3-dev python3-pip wget net-tools libssl-dev

# cd /home/ubuntu/behavioral-model && tmpdir=`mktemp -d -p .` && cd $tmpdir && pwd && bash ../ci/install-thrift.sh


# THIS_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
# source $THIS_DIR/common.sh

# check_lib libthrift libthrift-0.13.0

set -e
# Make it possible to get thrift in China
# wget http://archive.apache.org/dist/thrift/0.13.0/thrift-0.13.0.tar.gz
# tar -xzvf thrift-0.13.0.tar.gz
git clone -b 0.13.0 https://github.com/apache/thrift.git thrift-0.13.0
cd thrift-0.13.0
./bootstrap.sh
./configure --with-cpp=yes --with-c_glib=no --with-java=no --with-ruby=no --with-erlang=no --with-go=no --with-nodejs=no
make -j32 && sudo make install
cd lib/py
sudo python3 setup.py install



cd /home/ubuntu/behavioral-model && tmpdir=`mktemp -d -p .` && cd $tmpdir && pwd  && bash ../ci/install-nanomsg.sh && sudo ldconfig && bash ../ci/install-nnpy.sh && cd .. &&  sudo rm -rf $tmpdir
cd /home/ubuntu/behavioral-model && ./autogen.sh && ./configure --without-nanomsg --disable-elogger --disable-logging-macros 'CFLAGS=-g -O2' 'CXXFLAGS=-g -O2' && make -j 32 &&  sudo make install && sudo ldconfig

. /etc/os-release && echo "deb https://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${VERSION_ID}/ /" | sudo tee /etc/apt/sources.list.d/home:p4lang.list && curl -L "https://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${VERSION_ID}/Release.key" | sudo apt-key add - && sudo apt-get update && sudo apt install -y p4lang-p4c
