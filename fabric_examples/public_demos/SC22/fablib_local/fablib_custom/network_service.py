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


class NetworkService_Custom():
    def place_holder():
        pass

    def get_userdata(self):
        return list(filter(lambda x: x['name'] ==  self.get_name(), self.get_slice().userdata['networks']))[0]
    
    def allocate_ip(self):
        try:
            network_userdata = self.get_userdata()
            
            ip_list = []
            gateway = IPv4Address(network_userdata['gateway'])
            for i in range(256):
                ip = gateway+i
                if str(ip) not in network_userdata['allocated_ips']:
                    network_userdata['allocated_ips'].append(str(ip))
                    break
            return ip
        except Exception as e:
            #logging.warning(f"Failed to ip: {e}")
            print(e)
            return None
        
    def set_subnet(self, subnet):
        
        print(f"layer: {self.get_layer()}")
        if str(self.get_layer()) == 'L2':
            network_userdata = self.get_userdata()
            
            network_userdata['subnet'] = subnet
            network_userdata['allocated_ips'] = []
        else:
            logging.warning("Cannot set subnet for L3 network")
            

    def set_gateway(self, gateway):
        if str(self.get_layer()) == 'L2':
            network_userdata = self.get_userdata()
            
            network_userdata['gateway'] = gateway
            network_userdata['allocated_ips'].append(gateway)

        else:
            logging.warning("Cannot set subnet for L3 network")
            
            
# Add methods to FABlib Classes
from fabrictestbed_extensions.fablib.network_service import NetworkService

#fablib.Slice
setattr(NetworkService, 'allocate_ip', NetworkService_Custom.allocate_ip )
setattr(NetworkService, 'get_userdata', NetworkService_Custom.get_userdata )

setattr(NetworkService, 'set_gateway', NetworkService_Custom.set_gateway )
setattr(NetworkService, 'set_subnet', NetworkService_Custom.set_subnet )


            
