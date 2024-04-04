#!/bin/bash
set -eu

sudo apt-get -y update
sudo apt-get -y install --no-install-recommends openvpn bird socat psmisc ipcalc
sudo systemctl disable bird bird6 openvpn
sudo systemctl stop bird bird6 openvpn

chmod 400 /home/ubuntu/client/certs/client.*
