#!/bin/bash

devs=$@

cwd=`pwd`

path=$(dirname "$0")

echo $path

${path}/node_tools/save_iface_config.py -d ${path}/ip_config/ifaces $devs 
${path}/node_tools/save_route_config.py -d ${path}/ip_config/routes -f routes.json 
cd ${path}; docker compose up -d ; cd $cwd
sleep 30
sudo ${path}/node_tools/config_netns.py -c frrouting -n frrouting 
sudo ${path}/node_tools/set_netns_ifaces.py -n frrouting $devs
#sudo ip netns exec frrouting  ${path}/node_tools/config_ifaces.py ip_config/ifaces/eth*.json 
#sudo ip netns exec frrouting  
docker exec frrouting sh -c './config/node_tools/config_ifaces.py ./config/ip_config/ifaces/eth*.json' 
docker exec frrouting sh -c './config/node_tools/config_routes.py ip_config/routes/routes.json'
#docker exec frrouting sh -c 'sudo ./tools/host_tune_redhat.sh'
docker exec -d -it frrouting sh -c 'sudo /usr/libexec/frr/frrinit.sh start'

cd $cwd