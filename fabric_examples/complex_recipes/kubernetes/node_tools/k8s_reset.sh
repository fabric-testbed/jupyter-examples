#!/bin/bash
set -e

# Reset the Kubernetes control plane setup
sudo kubeadm reset -f

# Remove leftover config and state
sudo rm -rf /etc/kubernetes/
sudo rm -rf /var/lib/etcd/
sudo rm -rf ~/.kube

# Free the ports by restarting containerd or rebooting
sudo systemctl restart containerd

