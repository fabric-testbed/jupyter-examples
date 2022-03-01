#!/bin/bash

{ 
echo Hello, FABRIC from node `hostname -s`
sudo apt-get update
sudo apt-get install -y docker.io
docker run -d -it --cap-add=NET_ADMIN --privileged --name fabric_p4 pruth/fabric-images:fabric_p4_simple_router
# ???? docker run -d -it fabric_p4 --device /dev/
sleep 10
NSPID=\$(docker inspect --format='{{ .State.Pid }}' fabric_p4) 
echo NSPID \$NSPID
ip link set dev ens7 promisc on
ip link set dev ens8 promisc on 
ip link set dev ens9 promisc on 
ip link set dev ens10 promisc on 
ip link set ens7 netns \$NSPID 
ip link set ens8 netns \$NSPID 
ip link set ens10 netns \$NSPID 
docker exec fabric_p4 ip link set dev ens7 up
docker exec fabric_p4 ip link set dev ens8 up 
docker exec fabric_p4 ip link set dev ens10 up
docker exec fabric_p4 ip link set dev ens7 promisc on 
docker exec fabric_p4 ip link set dev ens8 promisc on 
docker exec fabric_p4 ip link set dev ens10 promisc on 
#docker exec fabric_p4 sysctl net.ipv6.conf.ens7.disable_ipv6=1 
#docker exec fabric_p4 sysctl net.ipv6.conf.ens8.disable_ipv6=1 
#docker exec fabric_p4 sysctl net.ipv6.conf.ens10.disable_ipv6=1 
echo Starting switch
#docker exec -d -it fabric_p4 sh -c 'simple_switch --interface 0@ens7 --interface 1@ens8 --interface 2@ens10 /root/simple_p4_router/simple_router.bmv2/simple_router.json' 
#docker exec -it fabric_p4 simple_switch_CLI 
echo done! 
} 2>&1 > /tmp/script.log 
