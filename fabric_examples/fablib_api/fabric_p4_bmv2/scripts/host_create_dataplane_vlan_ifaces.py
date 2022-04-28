#!/usr/bin/python3

import netifaces
import os
import sys
import subprocess
import netifaces
import json
from pprint import pprint


#hostname = os.system('hostname -s')
#os.system("echo Hello from {}".format(hostname))
hostname = subprocess.check_output('hostname -s', shell=True)
hostname = str(hostname,'utf-8').replace('\n','')
#print(f"Hello from {hostname}")


IPV4=2
IPV6=10
ETHERNET=17
DEFAULT='default'

vlan = sys.argv[1]

return_data = {}

#Gateways
#gateways = netifaces.gateways()


interfaces_with_ipv4_gw = []
for gw_type, gw in netifaces.gateways().items():
    if gw_type == IPV4:
        #print('IPv4 Gateway: {}'.format(gw))
        for ip, iface, up in gw:
            #print("IP: {}, iface: {}, up: {}".format(ip,iface,up))
            interfaces_with_ipv4_gw.append( (iface,ip) )


#print("management interface(s): {}".format(interfaces_with_ipv4_gw))
return_data['management'] = []
for iface in interfaces_with_ipv4_gw:
    return_data['management'].append(iface)

#print(return_data)

#Interfaces
dataplane_interfaces = netifaces.interfaces()
dataplane_interfaces.remove('lo')
for iface,ip in interfaces_with_ipv4_gw:
    dataplane_interfaces.remove(iface)

#print("dataplane interface(s): {}".format(dataplane_interfaces))


# Create dataplan vlan ifaces
for iface in dataplane_interfaces:
    os.system(f'sudo ip link add link {iface} name {iface}.{vlan} type vlan id {vlan}')
    os.system(f'sudo ip link set dev {iface}.{vlan} up')

print(json.dumps(return_data))
