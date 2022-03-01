#!/usr/bin/python3

import netifaces
import os
import sys
import subprocess
from pprint import pprint

#os.system("echo Hello from the node!")

IPV4=2
IPV6=10
ETHERNET=17
DEFAULT='default'

#print ('Number of arguments: '+str(len(sys.argv))+' arguments.')
#print ('Argument List: '+str(sys.argv))

net_name = sys.argv[1]
dataplane_ip = sys.argv[2]
dataplane_cidr = sys.argv[3]
target_dataplane_ip = sys.argv[4]


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

#print("management interface(s): {}".format(interfaces_with_ipv4_gw))

#Interfaces
dataplane_interfaces = netifaces.interfaces()
dataplane_interfaces.remove('lo')
for iface in interfaces_with_ipv4_gw:
    dataplane_interfaces.remove(iface)

#print("dataplane interface(s): {}".format(dataplane_interfaces))

# Flush all dataplane_interfaces
for iface in dataplane_interfaces:
    #print("Flush iface: {}".format(iface))
    os.system('sudo ip addr flush dev '+str(iface))

#Test all dataplane_interfaces for connection to known server
for iface in dataplane_interfaces:
    #print("Iface: {}".format(iface))
    found = False

    host_name = subprocess.check_output('hostname -s', shell=True)
    host_name = str(host_name,'utf-8').replace('\n','')

    os.system('sudo ip addr flush dev '+str(iface))
    os.system('sudo ip addr add ' + dataplane_ip +'/' + dataplane_cidr + ' dev '+str(iface))
    os.system('sudo ip link set dev '+ str(iface) + ' up mtu 9000')


    if os.system('ping -c 3 ' + target_dataplane_ip + ' 2>&1 > /dev/null' ) == 0:
        #print(", success! keeping configuration")
        #print("{}: {} -> {}".format(host_name,str(iface),net_name) )
        print("{}".format(str(iface)))
        found = True
        #iface_list.remove(iface)
        #break
    #else:
        #print(", fail!")

    os.system('sudo ip addr flush dev '+str(iface))

    if found:
        break


if not found:
    #print("{}: {} -> Not Found".format(host_name,str(iface),net_name) )
    print("None")
    #print("Router {} -> Not Found".format(str(iface)) )
