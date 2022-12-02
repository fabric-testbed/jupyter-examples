#!/bin/python3

import os

import json
import time
import paramiko


import pandas as pd
from tabulate import tabulate

import logging

from fabrictestbed.util.constants import Constants
from concurrent.futures import ThreadPoolExecutor

from fabrictestbed.slice_editor import (
    ExperimentTopology,
    Capacities
)


import select

#from fablib_local_imports.fablib_plugin_methods.node import *
#from fablib_local_imports.fablib_plugin_methods.interface import *
#from fablib_local_imports.fablib_plugin_methods.slice import *

class Node_Custom():

    def place_holder():
        pass

    def get_userdata(self):
        return list(filter(lambda x: x['name'] ==  self.get_name(), self.get_slice().userdata['nodes']))[0]
        
    def init_userdata(self):
        node_userdata = self.get_userdata()
        
        node_userdata['static_routes'] = []
    
    def add_static_route(self, subnet, gateway):
        
        try:
            slice_userdata = self.get_slice().get_userdata()
            node_userdata = self.get_userdata()

            print(f"slice_userdata: {json.dumps(slice_userdata, indent=4)}")
            print(f"node_userdata: {json.dumps(node_userdata, indent=4)  }")

            network_userdata = list(filter(lambda x: x['gateway'] == gateway, slice_userdata['networks']))[0]
            print(f"network_userdata: {json.dumps(network_userdata, indent=4)   }")

            interface_userdata = list(filter(lambda x: x['network'] == network_userdata['name'], slice_userdata['interfaces']))[0]
            print(f"interface_userdata: {json.dumps(interface_userdata, indent=4)   }")

            dev = interface_userdata['dev']
            print(f"dev: {dev}")

            if 'static_routes' not in node_userdata:
                node_userdata['static_routes'] = []

            node_userdata['static_routes'].append({ 'subnet': subnet, 'gateway': gateway })

            #gateway = network_userdata['gateway']
            self.execute( f'sudo nmcli connection mod {dev} +ipv4.routes "{subnet} {gateway}" ;'
                          f'sudo nmcli con down {dev} ;'
                          f'sudo nmcli con up {dev} ;', quiet=True)
        except Exception as e:
            logging.error(f"Faled to add static route {node.get_name()}, {subnet} {gatewau}")
        
    def upload_directory(self, local_directory_path: str, remote_directory_path: str, retry: int = 3,
                         retry_interval: int = 10):
        """
        Upload a directory to remote location on the node.
        Makes a gzipped tarball of a directory and uploades it to a node. Then
        unzips and tars the directory at the remote_directory_path
        :param local_directory_path: the path to the directory to upload
        :type local_directory_path: str
        :param remote_directory_path: the destination path of the directory on the node
        :type remote_directory_path: str
        :param retry: how many times to retry SCP upon failure
        :type retry: int
        :param retry_interval: how often to retry SCP on failure
        :type retry_interval: int
        :raise Exception: if management IP is invalid
        """
        import tarfile
        import os
        import tempfile

        
        logging.debug(f"upload node: {self.get_name()}, local_directory_path: {local_directory_path}")

        output_filename = local_directory_path.split('/')[-1]
        root_size = len(local_directory_path) - len(output_filename)
        
        temp_name = next(tempfile._get_candidate_names())

        temp_file = "/tmp/" + str(temp_name) + ".tar.gz"

        with tarfile.open(temp_file, "w:gz") as tar_handle:
            for root, dirs, files in os.walk(local_directory_path):
                for file in files:
                    tar_handle.add(os.path.join(root, file), arcname = os.path.join(root, file)[root_size:])

        self.upload_file(temp_file, temp_file, retry, retry_interval)
        os.remove(temp_file)
        self.execute("mkdir -p "+remote_directory_path + "; tar -xf " + temp_file + " -C " +
                     remote_directory_path + "; rm " + temp_file, retry, retry_interval, quiet=True)
        return "success"
        
# Add methods to FABlib Classes
from fabrictestbed_extensions.fablib.node import Node

#fablib.Node
setattr(Node, 'add_static_route', Node_Custom.add_static_route)
setattr(Node, 'get_userdata', Node_Custom.get_userdata)
setattr(Node, 'init_userdata', Node_Custom.init_userdata)
setattr(Node, 'upload_directory', Node_Custom.upload_directory)
#setattr(Node, 'execute', Node_Custom.execute)


