#!/bin/bash

# Linux host tuning from https://fasterdata.es.net/host-tuning/linux/
cat >> /etc/sysctl.conf <<EOL
# allow testing with buffers up to 128MB
net.core.rmem_max = 536870912 
net.core.wmem_max = 536870912 
# increase Linux autotuning TCP buffer limit to 64MB
net.ipv4.tcp_rmem = 4096 87380 536870912
net.ipv4.tcp_wmem = 4096 65536 536870912
# recommended default congestion control is htcp  or bbr
net.ipv4.tcp_congestion_control=bbr
# recommended for hosts with jumbo frames enabled
net.ipv4.tcp_mtu_probing=1
# recommended to enable 'fair queueing'
net.core.default_qdisc = fq
#net.core.default_qdisc = fq_codel
EOL

sysctl --system

# Turn on jumbo frames
for dev in `basename -a /sys/class/net/*`; do
    ip link set dev $dev mtu 9000
done
