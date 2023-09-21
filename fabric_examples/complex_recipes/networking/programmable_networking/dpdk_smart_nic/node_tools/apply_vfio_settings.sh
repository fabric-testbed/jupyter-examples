#!/bin/bash

# Load the vfio-pci module
sudo modprobe vfio-pci

# Load the vfio module with enable_unsafe_noiommu_mode
sudo modprobe vfio enable_unsafe_noiommu_mode=1

# Enable unsafe_noiommu_mode for the vfio module
sudo echo 1 > /sys/module/vfio/parameters/enable_unsafe_noiommu_mode

# Set dma_entry_limit for vfio_iommu_type1
sudo echo 512000 > /sys/module/vfio_iommu_type1/parameters/dma_entry_limit

# Create a systemd service unit to apply these changes at boot
sudo cat <<EOF > /etc/systemd/system/vfio-settings.service
[Unit]
Description=VFIO Settings

[Service]
Type=oneshot
ExecStart=/usr/local/bin/apply_vfio_settings.sh

[Install]
WantedBy=multi-user.target
EOF

# Create the apply_vfio_settings.sh script
sudo cat <<EOF > /usr/local/bin/apply_vfio_settings.sh
#!/bin/bash

# Load the vfio-pci module
modprobe vfio-pci

# Load the vfio module with enable_unsafe_noiommu_mode
modprobe vfio enable_unsafe_noiommu_mode=1

# Enable unsafe_noiommu_mode for the vfio module
echo 1 > /sys/module/vfio/parameters/enable_unsafe_noiommu_mode

# Set dma_entry_limit for vfio_iommu_type1
echo 512000 > /sys/module/vfio_iommu_type1/parameters/dma_entry_limit

echo "VFIO settings applied."
EOF

# Make the apply_vfio_settings.sh script executable
sudo chmod +x /usr/local/bin/apply_vfio_settings.sh

# Enable and start the systemd service
sudo systemctl enable vfio-settings.service
sudo systemctl start vfio-settings.service

sudo echo "VFIO settings applied and configured to persist across reboots."