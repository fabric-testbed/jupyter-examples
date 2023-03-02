#!/bin/bash

ip -j -p route list > routes.config  
docker stop fabric; docker rm fabric 
cd ~/docker_containers/fabric_multitool/; docker compose up -d 
cd ~/node_tools ; rm -f *.json ; chmod +x * 
sudo ./config_netns.py fabric fabric 
sudo ./move_iface.py --namespace fabric {devs} 
cd ~ ; sudo ip netns exec fabric  ./node_tools/config_ifaces.py node_tools/eth*.json 
cd ~/docker_containers/droppy ; docker compose up -d 
cd ~/docker_containers/fabric_frrouting ; docker compose up -d 
docker exec fabric sudo ./tools/host_tune_redhat.sh 
docker exec -d -it frrouting sudo /usr/libexec/frr/frrinit.sh start 