#!/bin/sh

DIR=$(dirname "$0")

PID_DIR='tunnel_pids'

cd $DIR

if [ $# -eq 3 ]; then
   target_vm=$1
   target_port=$2
   local_port=$3
else
   echo 'Enter Target FABRIC VM (ex: username@1.2.3.4)'
   read target_vm
   echo 'Enter Target Port Number (ex: 22)'
   read target_port
   echo 'Enter Local Port Number (ex: 5555)'
   read local_port
fi

# maybe add -fN for background
ssh -fN  -L 127.0.0.1:${local_port}:127.0.0.1:${target_port} -i slice_key -F ssh_config ${target_vm}

PID=$(pgrep -f "ssh.*${local_port}:127.0.0.1:${target_port}.*${target_vm}")

mkdir -p $PID_DIR

echo $PID
echo $PID >  ${PID_DIR}/ssh_tunnel_${target_vm}_${target_port}_${local_port}.pid
