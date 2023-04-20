#!/bin/bash



echo "Hello, FABRIC, dev: "$1 > post_boot_output.txt

sudo dnf install -y tcpdump