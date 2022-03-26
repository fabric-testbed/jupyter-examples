#!/bin/bash

subnet=$1
ip=$2

{

yes | sudo kubeadm reset

sudo kubeadm init --pod-network-cidr=${subnet} --apiserver-advertise-address=${ip}

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
kubectl get nodes

}  2>&1 | tee -a start_control_plane.log
