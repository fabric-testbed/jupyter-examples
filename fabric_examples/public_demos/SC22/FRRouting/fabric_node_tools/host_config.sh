#!/bin/bash

# Install Packages
sudo yum install -y -q net-tools iperf3 iproute-tc iftop apache2

# Setup keys for ssh between hosts. Here we use a keypair that is also available on Chameleon
cp private_config/my_chameleon_key* ~/.ssh/.
chmod 600 ~/.ssh/my_chameleon_key*
cat ~/.ssh/my_chameleon_key.pub >> ~/.ssh/authorized_keys 

# Start ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/my_chameleon_key


# Config NVMe device
MNT_POINT='/home/ubuntu/nvme_mnt'

sudo fdisk -l /dev/nvme*
sudo parted -s /dev/nvme0n1 mklabel gpt
sudo parted -s /dev/nvme0n1 print
sudo parted -s /dev/nvme0n1 print unit MB print free
sudo parted -s --align optimal /dev/nvme0n1 mkpart primary ext4 0% 960197MB
sudo lsblk /dev/nvme0n1
sudo mkfs.ext4 /dev/nvme0n1p1
sudo mkdir $MNT_POINT && sudo mount /dev/nvme0n1p1 $MNT_POINT
df -h $MNT_POINT

# Set permissions on nvme drive
sudo chown -R ubuntu $MNT_POINT

