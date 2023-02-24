#!/bin/sh

DIR=$(dirname "$0")

PID_DIR='tunnel_pids'

cd $DIR

if [ $# -eq 2 ]; then
   target=$1
   local=$2
else
   echo 'Enter Target FABRIC VM Port (ex: username@1.2.3.4:22)'
   read target
   echo 'Enter Local Port Number (ex: localhost:5555)'
   read local
fi


target_port=$(echo $target | rev | cut -d':' -f1 | rev)
target_host=$(echo $target | rev | cut -d':' -f2- | rev | tr -d "[" | tr -d "]")
local_port=$(echo $local | rev | cut -d':' -f1 | rev)
local_host=$(echo $local | rev | cut -d':' -f2- | rev | tr -d "[" | tr -d "]")


echo $target_host
echo $target_port
echo $local_host
echo $local_port 





# maybe add -fN for background
echo ssh -fN  -L ${local_host}:${local_port}:127.0.0.1:${target_port} -i slice_key -F ssh_config ${target_host}


ssh -fN  -L ${local_host}:${local_port}:127.0.0.1:${target_port} -i slice_key -F ssh_config ${target_host}

PID=$(pgrep -f "ssh.*${local_host}:${local_port}:127.0.0.1:${target_port}.*${target_host}")

mkdir -p $PID_DIR

echo $PID
echo $PID >  ${PID_DIR}/tunnel_${target}_${local}}.pid
