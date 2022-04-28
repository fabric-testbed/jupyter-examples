#!/usr/bin/python3

import netifaces
import os
import sys
import netifaces
from pprint import pprint




print ('Number of arguments: '+str(len(sys.argv))+' arguments.')
print ('Argument List: '+str(sys.argv))

node_dataplan_ip = sys.argv[1]
node_dataplan_cidr = sys.argv[2]

os.system("echo Hello from the other side!")

IPV4=2
IPV6=10
ETHERNET=17
DEFAULT='default'

        
#Gateways
#gateways = netifaces.gateways()


interfaces_with_ipv4_gw = []
for gw_type, gw in netifaces.gateways().items():
    if gw_type == IPV4:
        #print('IPv4 Gateway: {}'.format(gw))   
        for ip, iface, up in gw:
            #print("IP: {}, iface: {}, up: {}".format(ip,iface,up)) 
            interfaces_with_ipv4_gw.append(iface)
    #elif gw_type == IPV6:
    #    print('IPv6 Gateway: {}'.format(gw))          
    #elif gw_type == DEFAULT:
    #    print('Default Gateway: {}'.format(gw))
    #    
    #else: 
    #    print('Unkown Gateway Type {}: {}'.format(gw_type,gw))
    #
    #for address in addresses:
    #    print(address)

print("management interface(s): {}".format(interfaces_with_ipv4_gw))
      
#Interfaces
dataplane_interfaces = netifaces.interfaces()
dataplane_interfaces.remove('lo')
for iface in interfaces_with_ipv4_gw:
    dataplane_interfaces.remove(iface)

print("dataplane interface(s): {}".format(dataplane_interfaces))

# Flush all dataplane_interfaces
for iface in dataplane_interfaces:
    print("Flush iface: {}".format(iface))
    os.system('sudo ip addr flush dev '+str(iface))

#Test all dataplane_interfaces for connection to known server
iface = dataplane_interfaces[0]
print("Setting iface: {} -> {}/{}".format(iface,node_dataplan_ip,node_dataplan_cidr))

os.system('sudo ip addr flush dev '+str(iface))
os.system('sudo ip addr add ' + node_dataplan_ip +'/' + node_dataplan_cidr + ' dev '+str(iface))
os.system('sudo ip link set dev '+ str(iface) + ' up mtu 9000')



