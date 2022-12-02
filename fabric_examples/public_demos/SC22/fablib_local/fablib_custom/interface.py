#!/bin/python3

import os

import json
import time
import paramiko


import pandas as pd
from tabulate import tabulate

from fabrictestbed.util.constants import Constants
from concurrent.futures import ThreadPoolExecutor

from fabrictestbed.slice_editor import (
    ExperimentTopology,
    Capacities
)

from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network


class Interface_Custom():
    def place_holder():
        pass
   
    def add_ip(self, ip=None):
        network = self.get_network()
        iface_userdata = self.get_userdata()
        network_userdata = network.get_userdata()
        
        ip = network.allocate_ip()
        
        iface_userdata['ip'] = str(ip)
        iface_userdata['subnet'] = str(network_userdata['subnet'])
                
        subnet_cidr = iface_userdata['subnet'].split('/')[1]
        dev = self.get_device_name()
        gateway = network_userdata['gateway']
        #self.get_node().execute(f'sudo nmcli connection mod {dev} ipv4.method manual ip4 {iface_userdata["ip"]}/{subnet_cidr} ;'
        #              f'sudo nmcli connection mod {dev} +ipv4.routes "10.128.0.0/10 {gateway}" ;'
        #              f'sudo nmcli con down {dev} ;'
        #              f'sudo nmcli con up {dev} ;', quiet=True)
        
        self.get_node().execute(f'sudo nmcli connection mod {dev} ipv4.method manual ip4 {iface_userdata["ip"]}/{subnet_cidr} ;' 
                                f'sudo nmcli con down {dev} ;'
                                f'sudo nmcli con up {dev} ;', quiet=True)
        
        return ip
        
        
    def get_ip(self):
         return list(filter(lambda x: x['name'] == self.get_name(), self.get_slice().userdata['interfaces']))[0]['ip']

        
    def init_userdata(self):
        iface_userdata = self.get_userdata()
        
        iface_userdata['dev'] = self.get_device_name()

        
    def init_for_network_manager(self):
        dev = self.get_device_name()
        self.get_node().execute(f'sudo nmcli device set {dev} managed yes', quiet=True)
        self.get_node().execute(f'sudo nmcli connection add con-name {dev} autoconnect yes save yes ipv6.method disabled ipv4.method disabled  ifname {dev} type ethernet', quiet=True)

        
        
    def get_userdata(self):
        return list(filter(lambda x: x['name'] ==  self.get_name(), self.get_slice().userdata['interfaces']))[0]
        
        
    def get_device_name(self) -> str:
        """
         Gets a name of the device name on the node

         If the interface requires a FABRIC VLAN tag, the interface name returned
         will be the VLAN tagged interface name.

         :return: OS interface name
         :rtype: String
         """
        try:
            iface_userdata = self.get_userdata()
            
            if 'dev' in iface_userdata:
                return iface_userdata['dev']
            else:
                # logging.debug(f"iface: {self}")
                os_iface = self.get_physical_os_interface_name()
                vlan = self.get_vlan()

                if vlan is not None:
                    os_iface = f"{os_iface}.{vlan}"
                    
                iface_userdata['dev'] = os_iface
        except:
            os_iface = None

        return os_iface
        
# Add methods to FABlib Classes
from fabrictestbed_extensions.fablib.interface import Interface


#fablib.Interface
setattr(Interface, 'get_userdata', Interface_Custom.get_userdata)
setattr(Interface, 'add_ip', Interface_Custom.add_ip)
setattr(Interface, 'init_for_network_manager', Interface_Custom.init_for_network_manager)
setattr(Interface, 'get_ip', Interface_Custom.get_ip)
setattr(Interface, 'init_userdata', Interface_Custom.init_userdata)
setattr(Interface, 'get_device_name', Interface_Custom.get_device_name)
