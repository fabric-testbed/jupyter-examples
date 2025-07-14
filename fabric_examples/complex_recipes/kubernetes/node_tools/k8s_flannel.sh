#!/bin/bash

set -e

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <API_SERVER_IP>"
  echo "Example: $0 10.129.4.2"
  exit 1
fi

API_SERVER_IP="$1"
API_SERVER_PORT="6443"

echo "Deleteing Flannel CNI..."
kubectl delete -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml >/dev/null 2>&1 || true

echo "Installing Flannel CNI..."
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

echo "Waiting for Flannel DaemonSet to be created..."
while ! kubectl -n kube-flannel get daemonset kube-flannel-ds >/dev/null 2>&1; do
  sleep 1
done

echo "Patching Flannel..."

kubectl -n kube-flannel get daemonset kube-flannel-ds -o json | \
jq --arg iface "$INTERFACE" \
 --arg api_ip "$API_SERVER_IP" \
 --arg api_port "$API_SERVER_PORT" \
'
.spec.template.spec.containers |= map(
if .name == "kube-flannel" then
  .args = ["--ip-masq", "--kube-subnet-mgr", "--iface-can-reach=\($api_ip)"] |
  .env |=
    map(select(.name != "KUBERNETES_SERVICE_HOST" and .name != "KUBERNETES_SERVICE_PORT")) +
    [
      { "name": "KUBERNETES_SERVICE_HOST", "value": $api_ip },
      { "name": "KUBERNETES_SERVICE_PORT", "value": $api_port }
    ]
else . end
)
' | kubectl apply -f -

echo "Restarting Flannel pods..."
kubectl -n kube-flannel delete pods --all

echo "Flannel installed and patched."
