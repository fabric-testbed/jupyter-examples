#!/bin/bash

# Check for root
if [[ $EUID -ne 0 ]]; then
  echo "Please run as root or use sudo"
  exit 1
fi

# Check for argument
if [[ -z "$1" ]]; then
  echo "Usage: $0 <IP_ADDRESS>"
  exit 1
fi

mkdir -p /etc/default

NODE_IP="$1"
CONF_FILE="/etc/default/kubelet"

# Set or update KUBELET_EXTRA_ARGS
echo "Setting KUBELET_EXTRA_ARGS=--node-ip=${NODE_IP}"
echo "KUBELET_EXTRA_ARGS=--node-ip=${NODE_IP}" > "$CONF_FILE"

# Reload and restart kubelet
echo "Reloading systemd and restarting kubelet..."
systemctl daemon-reexec
systemctl daemon-reload
systemctl restart kubelet

# Check status
echo "kubelet restarted with --node-ip=${NODE_IP}"
systemctl status kubelet --no-pager | grep -E "Active:|Loaded:"
