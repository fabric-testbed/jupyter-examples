#!/bin/bash

pgcnt="$1"

if [ -z "$pgcnt" ]; then
  echo "Usage: $0 <pgcnt>"
  exit 1
fi

sudo sed -i "s/GRUB_CMDLINE_LINUX=\"\(.*\)\"/GRUB_CMDLINE_LINUX=\"\1 amd_iommu=on iommu=pt default_hugepagesz=1G hugepagesz=1G hugepages=$pgcnt\"/" /etc/default/grub
sudo sed -i 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="amd_iommu=on iommu=pt default_hugepagesz=1G hugepagesz=1G hugepages=$pgcnt"/' /etc/default/grub

sudo grub2-mkconfig -o /boot/grub2/grub.cfg
sudo update-grub
