#!/bin/python3

import os

import json
import time
import paramiko

import logging

import pandas as pd
from tabulate import tabulate

from fabrictestbed.util.constants import Constants
from concurrent.futures import ThreadPoolExecutor

from fabrictestbed.slice_editor import (
    ExperimentTopology,
    Capacities
)

from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network


class Slice_Custom():

    def place_holder():
        pass

    
    def get_userdata(self):
        return self.userdata

    def init_userdata(self):
        self.userdata = self.get_template_context()
        
        for network in self.userdata['networks']:
            if network['type'] == 'FABNetv4' or network['type'] == 'FABNetv6':
                if 'gateway' in network:
                    network['allocated_ips'] = [network['gateway']]
                    
        for iface in self.get_interfaces():
            iface.init_userdata()
                    
    def init_network_manager(self):
        for node in self.get_nodes():
            management_device = node.get_management_device_name()
            #print(f"management_device: {management_device}")

            #node.execute(('nmcli con del $(nmcli -t -f UUID,DEVICE con | awk -F":" \'{if ($2 != "{}") print $1}\')').format(management_device)  )
            node.execute('sudo nmcli con del $(nmcli -t -f UUID,DEVICE con | awk -F":" \'{{ if ($2 != "{}") print $1 }}\') '.format(management_device), quiet=True)

        for iface in self.get_interfaces():
            iface.init_for_network_manager()
    


# Add methods to FABlib Classes
from fabrictestbed_extensions.fablib.slice import Slice

#fablib.Slice
setattr(Slice, 'init_userdata', Slice_Custom.init_userdata)
setattr(Slice, 'init_network_manager', Slice_Custom.init_network_manager)
setattr(Slice, 'get_userdata', Slice_Custom.get_userdata)

#setattr(Slice, 'get_slice_id', Slice_Custom.get_slice_id)
#setattr(Slice, 'list_nodes_pandas', Slice_Custom.list_nodes_pandas)
#setattr(Slice, 'list_nodes_tabulate', Slice_Custom.list_nodes_tabulate)
#setattr(Slice, 'list_nodes', Slice_Custom.list_nodes)

            
