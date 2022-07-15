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

# Flush all dataplane_interfaces
for iface in dataplane_interfaces:
    #print("Flush iface: {}".format(iface))
    os.system('sudo ip addr flush dev '+str(iface))

#Test all dataplane_interfaces for connection to known server
return_data['dataplane'] = []
subnet_num = 1
for iface in dataplane_interfaces:

    node_dataplan_ip = '192.168.'+str(subnet_num)+'.100'
    node_dataplan_cidr = '24'
    #print("Setting iface: {} -> {}/{}".format(iface,node_dataplan_ip,node_dataplan_cidr))

    return_data['dataplane'].append((iface,node_dataplan_ip))
    os.system('sudo ip addr flush dev '+str(iface))
    os.system('sudo ip addr add ' + node_dataplan_ip +'/' + node_dataplan_cidr + ' dev '+str(iface))
    os.system('sudo ip link set dev '+ str(iface) + ' up mtu 9000')
    subnet_num = subnet_num + 1

import pickle
#print(pickle.dumps(return_data,0).decode())

print(json.dumps(return_data))
