#!/bin/bash

set -e

# Check for IP argument
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <ctrlr_addr>"
  echo "Example: $0 10.129.4.2"
  exit 1
fi

CTRLR_ADDR="$1"

echo "🔧 Initializing Kubernetes control plane with address: $CTRLR_ADDR"

# Run kubeadm init
sudo kubeadm init \
  --control-plane-endpoint="$CTRLR_ADDR" \
  --apiserver-advertise-address="$CTRLR_ADDR" \
  --node-name=ctrlr \
  --pod-network-cidr=10.244.0.0/16

# Set up kubeconfig
echo "Setting up kubeconfig for current user..."
mkdir -p "$HOME/.kube"
sudo cp -i /etc/kubernetes/admin.conf "$HOME/.kube/config"
sudo chown "$(id -u):$(id -g)" "$HOME/.kube/config"

echo "Kubernetes control plane initialized and kubeconfig set"
