#!/bin/bash


ROUTER_ID=$1
shift
SUBNET_ALL_CIDR=$1   #format  1.2.3.4 255.255.0.0
shift
SUBNET_ALL=$1
shift
SUBNET_ALL_MASK=$1
shift

echo $ROUTER_ID
echo $SUBNET_ALL_CIDR
echo $SUBNET_ALL
echo $SUBNET_ALL_MASK
echo $@
{

sudo sudo dnf install -y epel-release
sudo /usr/bin/crb enable
sudo dnf install -y frr vim httpd iproute-tc net-tools pciutils tcpdump iftop iperf3 
#sudo yum install -y vim tcpdump frr iproute-tc net-tools 

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
#net.core.default_qdisc = fq
net.core.default_qdisc = fq_codel
EOL


sysctl --system




sudo sysctl -w net.ipv4.ip_forward=1

sudo sed -i 's/ospfd=no/ospfd=yes/g' /etc/frr/daemons

#Edit /etc/frr/zebra: add these lines
HOST_NAME=`hostname`

echo $HOST_NAME

#for i in $@; do
#   dev=`echo $i | cut -d ":" -f 1`
#   subnet=`echo $i | cut -d ":" -f 2`
#
#  echo $dev
#   echo $subnet
#   
#   chmod +x fabric_node_tools/host_tune_redhat.sh
#   ./fabric_node_tools/host_tune_redhat.sh $dev
#done


#Edit /etc/frr/zebra: add these lines
cat > /etc/frr/zebra.conf <<EOL
hostname ${HOST_NAME}
log file /var/log/zebra.log
EOL

for i in $@; do
   dev=`echo $i | cut -d ":" -f 1`
   subnet=`echo $i | cut -d ":" -f 2`
cat >> /etc/frr/zebra.conf <<EOL
!
interface ${dev}
 ip address ${subnet}
EOL
done


cat > /etc/frr/ospfd.conf  <<EOL
hostname ${HOST_NAME}
log file /var/log/ospfd.log
EOL


for i in $@; do
   dev=`echo $i | cut -d ":" -f 1`
   subnet=`echo $i | cut -d ":" -f 2`
cat >> /etc/frr/ospfd.conf <<EOL
!
interface ${dev}
 ip ospf hello-interval 10
 ip ospf dead-interval 20
EOL
done



cat >> /etc/frr/ospfd.conf  <<EOL
!
!
router ospf
 ospf router-id ${ROUTER_ID}
 log-adjacency-changes
 redistribute kernel
 redistribute connected
 redistribute static
 network ${SUBNET_ALL_CIDR} area 1
 access-list 20 permit ${SUBNET_ALL} ${SUBNET_ALL_MASK}
 access-list 20 deny any
!
line vty
EOL

sudo systemctl daemon-reload
#sudo systemctl start frr.service
sudo systemctl restart frr.service

} 2>&1 > frr_config.log  