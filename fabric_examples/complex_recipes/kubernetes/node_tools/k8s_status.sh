#!/bin/bash

echo "Nodes:"
kubectl get nodes -o wide
echo

echo "All Pods:"
kubectl get pods --all-namespaces -o wide
echo

echo "All Services:"
kubectl get svc -o wide