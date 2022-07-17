#!/bin/bash

#{
#port1_iface=$1
#port2_iface=$2
#port3_iface=$3
#ip_type=$4

ip_type=$1
#args="${@:2:2}"
ifaces="${@:2}"


# export http_proxy=socks5h://localhost:4567
# export https_proxy=socks5h://localhost:4567

echo Hello, FABRIC. From node `hostname -s`
sudo apt-get update
sudo apt-get install -y docker.io
# docker run -d -it --cap-add=NET_ADMIN --privileged --name fabric_p4 pruth/fabric-images:fabric_p4_simple_router

if [ $ip_type = 'IPv4' ]
then
  docker run -d -it --cap-add=NET_ADMIN --privileged --name fabric_p4 registry.ipv4.docker.com/pruth/fabric-images:0.0.2j
else
  docker run -d -it --cap-add=NET_ADMIN --privileged --name fabric_p4 registry.ipv6.docker.com/pruth/fabric-images:0.0.2j
  sed -i '/nameserver/d' /etc/resolv.conf 
  echo nameserver 2a00:1098:2c::1 >> /etc/resolv.conf 
  echo nameserver 2a01:4f8:c2c:123f::1 >> /etc/resolv.conf 
  echo nameserver 2a00:1098:2b::1 >> /etc/resolv.conf 
fi

sleep 10
NSPID=$(docker inspect --format='{{ .State.Pid }}' fabric_p4)
echo NSPID $NSPID

switch_interface_args=""
swtich_port=0
for iface in $ifaces; do
  ip link set dev $iface promisc on
  ip link set $iface netns $NSPID
  docker exec fabric_p4 ip link set dev $iface up
  docker exec fabric_p4 ip link set dev $iface promisc on
  docker exec fabric_p4 sysctl net.ipv6.conf.${iface}.disable_ipv6=1

  switch_interface_args="${switch_interface_args} --interface ${swtich_port}@${iface}"
  swtich_port=$((swtich_port+1))
done


echo Starting switch
#echo simple_switch $switch_interface_args /root/simple_p4_router/simple_router.bmv2/simple_router.json
#complite
docker exec -w /root/tutorials/exercises/basic_tunnel fabric_p4 sh -c 'cp basic_tunnel.p4 basic_tunnel.working.p4'
docker exec -w /root/tutorials/exercises/basic_tunnel fabric_p4 sh -c 'cp solution/basic_tunnel.p4 basic_tunnel.p4'
docker exec -w /root/tutorials/exercises/basic_tunnel fabric_p4 sh -c 'p4c --p4runtime-files basic_tunnel.txt --target bmv2 --arch v1model basic_tunnel.p4'
docker exec -d -it fabric_p4 sh -c 'simple_switch --interface 1@'${port1_iface}' --interface 2@'${port2_iface}' --interface 3@'${port3_iface}' /root/tutorials/exercises/basic_tunnel/basic_tunnel.json'
#docker exec -it fabric_p4 simple_switch_CLI
#sudo sh -c 'cat commands.txt | docker exec -i fabric_p4 simple_switch_CLI --thrift-port 9090
#sudo sh -c 'echo table_dump myTunnel_exact | docker exec -i fabric_p4 simple_switch_CLI --thrift-port 9090 '

echo done!
#} 2>&1 > /tmp/script.log
