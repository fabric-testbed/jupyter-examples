#!/bin/python3
import os

#General imports
import os
import json
import traceback
from ipaddress import ip_address, IPv4Address, IPv6Address, IPv4Network, IPv6Network
from datetime import datetime, timedelta
from dateutil import tz
import time

# Chameleon Library
from chi.server import *
from chi.lease import *
from chi.network import *

import chi
import chi.lease 

# FABRIC Library
from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager

BLAZAR_TIME_FORMAT = '%Y-%m-%d %H:%M'

default_chameleon_image_name='CC-CentOS8-stream'
default_chameleon_node_type="compute_cascadelake_r"
default_chameleon_server_count=1
default_chameleon_key_name='my_chameleon_key'



def create_chameleon_servers(name='chameleon_servers', 
                              count=default_chameleon_server_count, 
                              node_type=default_chameleon_node_type,
                              image_name=default_chameleon_image_name,
                              key_name=default_chameleon_key_name,
                              network_name=None,
                              lease=None, compute_reservation_id=None):
    
    if lease == None and compute_reservation_id == None:
        print(f"Creating lease {name}")
        lease = create_chameleon_server_lease(name=name, 
                                      count=count, 
                                      node_type=node_type,
                                      image_name=image_name,
                                      key_name=key_name,
                                      network_name=network_name)
          
        compute_reservation_id = [reservation for reservation in lease['reservations'] if reservation['resource_type'] == 'physical:host'][0]['id']
    print(f"Compute reservation_id {compute_reservation_id}")
    
    #wait 
          
    # Create the servers
    server = chi.server.create_server(name, 
                                  reservation_id=compute_reservation_id, 
                                  network_name=network_name, 
                                  image_name=image_name,
                                  key_name=key_name,
                                  count=count
                                 )
    
    print(f'Waiting for server fixed IPs .', end='')
    while True:
        try:
            if count == 1:
                server_id = chi.server.get_server_id(f'{name}')
            else:
                server_id = chi.server.get_server_id(f'{name}-1')

            #server = chi.server.get_server(f'{name}-1')
            #try to get the fixed ip. retry on failure
            chi.server.get_server(server_id).interface_list()[0].to_dict()["fixed_ips"][0]["ip_address"]
            print('done!')
            break;
        except Exception as e: 
            #print(str(e))
            print('.', end='')
            pass
        time.sleep(10)
        
    return server_id
          
def delete_chameleon_servers(name='chameleon_servers'):
    
    chi.lease.delete_lease(name)
    
    
def create_chameleon_server_lease(name='chameleon_servers', 
                                  count=default_chameleon_server_count, 
                                  node_type=default_chameleon_node_type,
                                  image_name=default_chameleon_image_name,
                                  key_name=default_chameleon_key_name,
                                  network_name=None,
                                  wait=True):
    # Set start/end date for lease
    # Start one minute into future to avoid Blazar thinking lease is in past
    # due to rounding to closest minute.
    start_date = (datetime.now(tz=tz.tzutc()) + timedelta(minutes=1)).strftime(BLAZAR_TIME_FORMAT)
    end_date   = (datetime.now(tz=tz.tzutc()) + timedelta(days=1)).strftime(BLAZAR_TIME_FORMAT)

    # Build list of reservations (in this case there is only one reservation)
    reservation_list = []
    chi.lease.add_node_reservation(reservation_list, count=count, node_type=node_type)


    # Create the lease
    lease = chi.lease.create_lease(name,
                                      reservations=reservation_list,
                                      start_date=start_date,
                                      end_date=end_date)
     
        
    if wait:
        print(f'Waiting for Chameleon lease .', end='')
        while True:
            try:
                #Get the network
                lease = chi.lease.get_lease(name)
                
                #print(f"{lease}")

                if lease['status'] == 'ACTIVE': 
                    break
                
                print(f'.', end='')
                
                time.sleep(10)
            except Exception as e:
                print(f'.', end='')                
                print(f"{e}")
                time.sleep(10)           
    print(f'done.')
    
    return lease



