#!/bin/bash

devs=$@

cwd=`pwd`

path=$(dirname "$0")

echo $path

${path}/node_tools/save_iface_config.py -d ${path}/ip_config/ifaces $devs 
${path}/node_tools/save_route_config.py -d ${path}/ip_config/routes -f routes.json 
cd ${path}; docker compose up -d ; cd $cwd
sudo ${path}/node_tools/config_netns.py -c fabric -n fabric 
sudo ${path}/node_tools/set_netns_ifaces.py -n fabric $devs
sudo ip netns exec fabric  ${path}/node_tools/config_ifaces.py ${path}/ip_config/ifaces/eth*.json 
sudo ip netns exec fabric  ${path}/node_tools/config_routes.py ${path}/ip_config/routes/routes.json
sudo ip netns exec fabric  ${path}/node_tools/host_tune.sh 

#docker exec frrouting sh -c './config/node_tools/config_ifaces.py ./config/ip_config/ifaces/eth*.json' 
#docker exec frrouting sh -c './config/node_tools/config_routes.py ip_config/routes/routes.json'
#docker exec frrouting sh -c 'sudo ./tools/host_tune_redhat.sh'
#docker exec -d -it frrouting sh -c 'sudo /usr/libexec/frr/frrinit.sh start'
#docker exec frrouting sh -c './config/node_tools/host_tune.sh'

cd $cwd