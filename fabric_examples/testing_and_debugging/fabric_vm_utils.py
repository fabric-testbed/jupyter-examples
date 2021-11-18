#!/usr/bin/python3

import netifaces
import os
import sys
import netifaces
from pprint import pprint

def get_management_iface():
    IPV4=2
    IPV6=10
    ETHERNET=17
    DEFAULT='default'

    node_dataplan_ip = sys.argv[2]
    node_dataplan_cidr = sys.argv[3]

    interfaces_with_ipv4_gw = []
    for gw_type, gw in netifaces.gateways().items():
        if gw_type == IPV4:
            #print('IPv4 Gateway: {}'.format(gw))
            for ip, iface, up in gw:
                #print("IP: {}, iface: {}, up: {}".format(ip,iface,up))
                interfaces_with_ipv4_gw.append(iface)

    return interfaces_with_ipv4_gw


def get_dataplane_ifaces():
    IPV4=2
    IPV6=10
    ETHERNET=17
    DEFAULT='default'

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
    return dataplane_interfaces

def flush_dataplane_ifaces():
    flush_ifaces(get_dataplane_ifaces())

def flush_ifaces(ifaces=[]):
    for iface in ifaces:
        print("Flush iface: {}".format(iface))
        os.system('sudo ip addr flush dev '+str(iface))

def set_iface_addr(ip=None, cidr=None, iface=None):

    #Interfaces
    #manegement_iface = get_management_iface()
    #dataplane_interfaces = get_dataplane_ifaces()

    #print("management interface(s): {}".format(manegement_iface))
    #print("dataplane interface(s): {}".format(dataplane_interfaces))

    # Flush all dataplane_interfaces
    flush_ifaces(ifaces=[iface])

    print("Setting iface: {} -> {}/{}".format(iface,ip,cidr))

    os.system('sudo ip addr flush dev '+str(iface))
    os.system('sudo ip addr add ' + ip +'/' + cidr + ' dev '+str(iface))
    os.system('sudo ip link set dev '+ str(iface) + ' up')


def create_vlan_iface(iface=None, vlan_tag=None):
    os.system('sudo ip link set dev ' + str(iface) + ' up')
    os.system('sudo ip link add link ' + str(iface) + ' name ' + str(iface) + '.' + str(vlan_tag) + ' type vlan id '+str(vlan_tag))

def delete_vlan_iface(iface=None, vlan_tag=None):
    #ip link add link eth1 name eth1.200 type vlan id 200
    #ip link set dev eth1.200 up
    #ip addr add 192.168.10.51/24 dev eth1.200
    print("delete_vlan_iface(iface=None, vlan_tag=None): {} {}".format(iface, vlan_tag))
    os.system('sudo ip link delete ' + str(iface)+'.'+str(vlan_tag))


def ping_test(server_ip=None, verbose=False):
    #def latency_test(self, ssh_client_n1, ssh_client_n2, dataplane_ip_n1, dataplane_ip_n2, verbose=False, info=None):
    if verbose: print("Testing Latency: {}".format(info),end='')

    #rtt min/avg/max/mdev = 0.063/0.119/0.189/0.053 ms
    #output = "Information about latency with ping: \n"

    #warm up
    #os.system('ping -c 3 ' + server_ip + ' | grep rtt 2&>1 > /dev/null')
    output = os.popen('cping -c 3 ' + server_ip + ' | grep rtt 2&>1 > /dev/null').read()
    #Real test
    #os.system('ping -c 10 ' + server_ip + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
    output = (os.popen('ping -c 10 ' + server_ip + " | tail -1| awk '{print $4}' | cut -d '/' -f 2").read()).replace('\n','')
    print("{}".format(output))
    return




def mtu_test(server_ip=None):
    pass

def iperf3_test(server_ip=None):
    pass

#print ('Number of arguments: '+str(len(sys.argv))+' arguments.')
#print ('Argument List: '+str(sys.argv))

command = sys.argv[1]
#node_dataplan_ip = sys.argv[2]
#node_dataplan_cidr = sys.argv[3]

#os.system("echo Hello from node")

if command == 'set_iface_addr':
    set_iface_addr(ip=sys.argv[2], cidr=sys.argv[3], iface=sys.argv[4])
elif command == 'flush_iface':
    print(flush_ifaces(ifaces=[sys.argv[2]]))
elif command == 'flush_all_ifaces':
    print(flush_ifaces(ifaces=get_dataplane_ifaces()))
elif command == 'get_datalane_ifaces':
    print(get_dataplane_ifaces())
elif command == 'get_management_iface':
    print(get_management_iface())
elif command == 'ping_test':
    ping_test(server_ip=sys.argv[2])
elif command == 'mtu_test':
    ping_test(server_ip=sys.argv[2])
elif command == 'iperf3_test':
    print(ping_test(server_ip=sys.argv[2]))
elif command == 'create_vlan_iface':
    print(create_vlan_iface(iface=sys.argv[2], vlan_tag=sys.argv[3]))
elif command == 'delete_vlan_iface':
    print(delete_vlan_iface(iface=sys.argv[2], vlan_tag=sys.argv[3]))
else:
    print("Unknown command: {}".foramt(str(command)))
