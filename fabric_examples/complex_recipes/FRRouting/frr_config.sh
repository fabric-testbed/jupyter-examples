#!/bin/bash


NIC_1=$1
NIC_2=$3
NIC_LOCAL=$5

IP_1=$2
IP_2=$4
IP_LOCAL=$6

SUBNET_ALL=$7

{

sudo yum install -y vim tcpdump frr
sudo sysctl -w net.ipv4.ip_forward=1

sudo sed -i 's/ospfd=no/ospfd=yes/g' /etc/frr/daemons


#Edit /etc/frr/zebra: add these lines
cat > /etc/frr/zebra.conf <<EOL
hostname $HOSTNAME 
log file /var/log/zebra.log
!
interface ${NIC_1}
 ip address ${IP_1}/24
!
interface ${NIC_2}
 ip address ${IP_2}/24 
!
interface ${NIC_LOCAL}
 ip address ${IP_LOCAL}/24
EOL



cat > /etc/frr/ospfd.conf  <<EOL
hostname hostname 870a0f89-9f62-4524-91e7-7ab79fc3928c-quagga-1.novalocal
log file /var/log/ospfd.log
!
interface ${NIC_1}
 ip ospf hello-interval 60
 ip ospf dead-interval 240
!
interface ${NIC_2}
 ip ospf hello-interval 60
 ip ospf dead-interval 240
!
interface ${NIC_LOCAL}
 ip ospf hello-interval 60
 ip ospf dead-interval 240
!
!
router ospf
 ospf router-id ${IP_LOCAL}
 log-adjacency-changes
 redistribute kernel
 redistribute connected
 redistribute static
 network ${SUBNET_ALL}/16 area 1
 access-list 20 permit ${SUBNET_ALL} 0.0.255.255
 access-list 20 deny any
!
line vty
EOL

sudo systemctl daemon-reload
sudo systemctl start frr.service

} 2>&1 > frr_config.log  