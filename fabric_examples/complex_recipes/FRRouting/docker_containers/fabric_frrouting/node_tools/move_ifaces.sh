#!/bin/bash

ip -j -p route list > routes.config  
docker stop fabric; docker rm fabric 
docker compose up -d 
sudo ./node_tools/config_netns.py fabric fabric 
sudo ./node_tools/move_iface.py --namespace fabric {devs} 
cd ~ ; sudo ip netns exec fabric  ./node_tools/config_ifaces.py node_tools/eth*.json 
docker exec fabric sudo ./tools/host_tune_redhat.sh 
docker exec -d -it frrouting sudo /usr/libexec/frr/frrinit.sh start 