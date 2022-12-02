#!/bin/python3

import json
import time
from ipaddress import ip_address, IPv4Address, IPv6Address, IPv4Network, IPv6Network

import traceback

from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager

def create_fabnet_slice(name='fabnet_slice', node_count=1, site=None, sites=[], cores=2, ram=8, disk=10, wait=True):
    
    #print(f"name: {name}, node_count {node_count}, {}, {}, {}, {}, {}")
    
    try:        
        fablib = fablib_manager(output_type='HTML')
        
        if len(sites) == 0:
            if site == None:
                sites = [ fablib.get_random_site() ]
            elif isinstance(site, str):
                sites = [ site ]
        
        #Create Slice
        slice = fablib.new_slice(name=name)
        
        for site in sites:
            ifaces = []
            net_name = f"{site}_net"
            
            if site == 'STAR':
                host_num = 5
            else:
                host_num = int(fablib.get_resources().get_cpu_capacity(site)/2)

            host = f"{site.lower()}-w{host_num}.fabric-testbed.net"
            for i in range(1,node_count+1):
                node_name = f"{site}_node{i}"
                node = slice.add_node(name=node_name, site=site, cores=cores, ram=ram, disk=disk, host=host)
                ifaces.append(node.add_component(model='NIC_Basic', name='nic1').get_interfaces()[0])

            # Network
            net = slice.add_l3network(name=net_name, interfaces=ifaces, type='IPv4')

        #Submit Slice Request
        slice.submit(progress=True)
        
        slice = fablib.get_slice(name=name)
        print(f"{slice}")
                
        for site in sites:
            ifaces = []
            net_name = f"{site}_net"
            net = slice.get_network(name=net_name)
            net_available_ips = net.get_available_ips()
            for i in range(1,node_count+1):
                node_name = f"{site}_node{i}"
                node = slice.get_node(node_name)
                node_iface = node.get_interface(network_name=net_name)  
                node_addr = net_available_ips.pop(0)
                node_iface.ip_addr_add(addr=node_addr, subnet=net.get_subnet())
                node.ip_route_add(subnet=IPv4Network("10.128.0.0/10") , gateway=net.get_gateway())
                print(f'{node.get_name()}: ip {node_addr}, subnet {net.get_subnet()}, host route: 10.128.0.0/10 via {net.get_gateway()}')
        return slice
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()
        
    return slice
    
def delete_fabnet_slice(name=None):
    fablib = fablib_manager()
    fablib.delete_slice(name)
    