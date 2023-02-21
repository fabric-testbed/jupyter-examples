#!/bin/sh

DIR=$(dirname "$0")

cd $DIR

echo 'Enter Target FABRIC VM (ex: username@1.2.3.4)'
read target_vm
echo 'Enter Target Port Number (ex: 22)'
read target_port
echo 'Enter Local Port Number (ex: 5555)'
read local_port

ssh -L 127.0.0.1:${local_port}:127.0.0.1:${target_port} -i slice_key -F ssh_config ${target_vm}
