#!/bin/bash
set -e

echo "==> Cleaning old Kubernetes APT sources and keyrings..."
sudo rm -f /etc/apt/sources.list.d/kubernetes.list
sudo rm -f /etc/apt/keyrings/kubernetes-*.gpg
sudo rm -f /usr/share/keyrings/kubernetes-archive-keyring.gpg
sudo rm -f /etc/apt/trusted.gpg.d/kubernetes-archive-keyring.gpg

echo "==> Updating package index and installing dependencies..."
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg

echo "==> Creating keyring directory..."
sudo mkdir -p -m 755 /etc/apt/keyrings

echo "==> Fetching new Kubernetes GPG key..."
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.33/deb/Release.key \
  | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo "==> Adding modern Kubernetes APT repository..."
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.33/deb/ /' \
  | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo chmod 644 /etc/apt/sources.list.d/kubernetes.list

echo "==> Updating APT and installing kubelet, kubeadm, kubectl..."
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl

echo "==> Holding versions to avoid accidental upgrades..."
sudo apt-mark hold kubelet kubeadm kubectl

echo "  Installed versions:"
echo "    kubelet:  $(kubelet --version 2>/dev/null || echo 'not found')"
echo "    kubeadm:  $(kubeadm version -o short 2>/dev/null || echo 'not found')"
echo "    kubectl:  $(kubectl version --client|| echo 'not found')"