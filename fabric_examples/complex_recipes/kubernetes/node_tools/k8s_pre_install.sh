#!/bin/bash

# Update package index and upgrade all packages
sudo apt update
sudo apt dist-upgrade -y

# Install containerd if not installed
if ! command -v containerd &> /dev/null; then
    sudo apt install -y containerd
fi

sudo apt install -y jq net-tools

# Create containerd config and enable systemd cgroup
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml > /dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf

sudo sysctl -w net.ipv6.conf.default.forwarding=1
echo 'net.ipv6.conf.default.forwarding=1' | sudo tee -a /etc/sysctl.conf

# Load br_netfilter module and ensure it persists
echo 'br_netfilter' | sudo tee /etc/modules-load.d/k8s.conf

sudo modprobe br_netfilter
sudo modprobe overlay

cat <<EOF | sudo tee /etc/sysctl.d/99-k8s-network.conf
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF

sudo sysctl --system


# Reboot to apply all changes
sudo reboot
