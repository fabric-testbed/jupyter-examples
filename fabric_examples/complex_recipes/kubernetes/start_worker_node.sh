#!/bin/bash

ip=$1

{

echo ${ip}

yes | sudo kubeadm reset

sudo kubeadm join ${ip}:6443 --token 6lnr2t.111a83z168va4w7a --discovery-token-ca-cert-hash   sha256:a473c0a0ee8641d477f324a4bfe98dcba02ae4f36fff449532aa31f2d9a20167

}  2>&1 | tee -a start_worker_node.log
