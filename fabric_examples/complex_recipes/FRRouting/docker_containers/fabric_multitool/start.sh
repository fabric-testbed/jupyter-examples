#!/bin/bash

devs=$@

cwd=`pwd`

path=$(dirname "$0")

container='fabric'
netns='fabric'

${path}/node_tools/save_iface_config.py -d ~/ip_config/ifaces $devs 
${path}/node_tools/save_route_config.py -d ~/ip_config/routes -f routes.json 
cd $path; docker compose up -d 
sudo ${path}/node_tools/config_netns.py -c ${container} -n ${netns} 
sudo ${path}/node_tools/set_netns_ifaces.py -n ${netns}  $devs
#sudo ip netns exec fabric  ${path}/node_tools/config_ifaces.py ip_config/ifaces/eth*.json 
#sudo ip netns exec fabric  ${path}/node_tools/config_routes.py ip_config/routes/routes.json 
docker exec frrouting sh -c './config/node_tools/config_ifaces.py ./config/ip_config/ifaces/eth*.json' 
docker exec frrouting sh -c './config/node_tools/config_routes.py ip_config/routes/routes.json'
#docker exec ${container} sudo ./tools/host_tune_redhat.sh 

cd $cwd