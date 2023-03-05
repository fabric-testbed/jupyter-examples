#!/bin/bash

cwd=`pwd`

path=$(dirname "$0")/..

cd $path

NIC_1=$1
IP_1=$2


HOSTNAME=$(hostname)


{


#Edit /etc/frr/zebra: add these lines
cat >> frr/zebra.conf <<EOL
!
interface ${NIC_1}
 ip address ${IP_1}/24
EOL



cat >> frr/ospfd.conf  <<EOL
!
interface ${NIC_1}
 ip ospf hello-interval 60
 ip ospf dead-interval 240
EOL

#sudo systemctl daemon-reload
#sudo systemctl start frr.service
#/usr/libexec/frr/frrinit.sh start

} 2>&1 >> frr_config.log  

cd $cwd