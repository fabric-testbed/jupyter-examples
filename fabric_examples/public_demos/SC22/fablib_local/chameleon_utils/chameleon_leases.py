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

default_chameleon_image_name='CC-Ubuntu20.04'
default_chameleon_node_type="compute_cascadelake_r"
default_chameleon_server_count=1
default_chameleon_key_name='my_chameleon_key'

def wait_for_chameleon_lease(name):
    print(f'Waiting for Chameleon lease .', end='')
    while True:
        try:
            #Get the network
            lease = chi.lease.get_lease(name)

            #print(f"{lease}")
            if lease['status'] == 'ERROR': 
                break
            
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
    

def delete_chameleon_lease(name):
    chi.lease.delete_lease(name)


def create_chameleon_server_lease(name, 
                                  count=default_chameleon_server_count, 
                                  node_type=default_chameleon_node_type,
                                  image_name=default_chameleon_image_name,
                                  key_name=default_chameleon_key_name,
                                  network_name=None,
                                  wait=True, retry=5, interval=20):
    while retry > 0:
        retry = retry - 1
        
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
            lease = wait_for_chameleon_lease(name)
            if lease['status'] == 'ACTIVE':
                break
            delete_chameleon_lease(name)
            print(f"lease['status'] = {lease['status']}, retrying...")
            time.sleep(interval)
            
        else:
            break
            
    return lease

def create_chameleon_stitched_network_lease(name, stitch_provider='fabric', wait=True, retry=5, interval=20):
    import chi
    import chi.lease 
    
    lease_name=name
    network_name=name
     
    while retry > 0:
        retry = retry - 1
        
        # Set start/end date for lease
        # Start one minute into future to avoid Blazar thinking lease is in past
        # due to rounding to closest minute.
        start_date = (datetime.now(tz=tz.tzutc()) + timedelta(minutes=1)).strftime(BLAZAR_TIME_FORMAT)
        end_date   = (datetime.now(tz=tz.tzutc()) + timedelta(days=1)).strftime(BLAZAR_TIME_FORMAT)

        # Build list of reservations (in this case there is only one reservation)
        reservation_list = []
        print(f"FABRIC network reservation: name: {network_name}, stitch_provider: {stitch_provider}")
        reservation_list.append(
                {
                    "resource_type": "network",
                    "network_name": network_name,
                    "network_properties": "",
                    "resource_properties": json.dumps(
                        ["==", "$stitch_provider", stitch_provider]
                    ),
                }
        )

        # Create the lease
        lease = chi.lease.create_lease(lease_name,
                                          reservations=reservation_list,
                                          start_date=start_date,
                                          end_date=end_date)
        if wait:
            lease = wait_for_chameleon_lease(name)
            if lease['status'] == 'ACTIVE':
                break
            
            # Tempoary to keep erred vlans
            if lease['status'] == 'ERROR':
                break
            
            delete_chameleon_lease(name)
            print(f"lease['status'] = {lease['status']}, retrying...")
            time.sleep(interval)
            
        else:
            break
    
    return lease

def create_chameleon_storage_network_lease(name=None, wait=True, retry=5, interval=20):
    import chi
    import chi.lease 
    
    lease_name=name
    network_name=name
     
    while retry > 0:
        retry = retry - 1
        
        # Set start/end date for lease
        # Start one minute into future to avoid Blazar thinking lease is in past
        # due to rounding to closest minute.
        start_date = (datetime.now(tz=tz.tzutc()) + timedelta(minutes=1)).strftime(BLAZAR_TIME_FORMAT)
        end_date   = (datetime.now(tz=tz.tzutc()) + timedelta(days=1)).strftime(BLAZAR_TIME_FORMAT)

        # Build list of reservations (in this case there is only one reservation)
        reservation_list = []
        print(f"FABRIC network reservation: name: {network_name}, usage_type = storage")
        reservation_list.append(
                {
                    "resource_type": "network",
                    "network_name": network_name,
                    "network_properties": "",
                    "resource_properties": json.dumps(
                        ["==", "$usage_type", 'storage']
                    ),
                }
        )

        # Create the lease
        lease = chi.lease.create_lease(lease_name,
                                          reservations=reservation_list,
                                          start_date=start_date,
                                          end_date=end_date)
        if wait:
            lease = wait_for_chameleon_lease(name)
            if lease['status'] == 'ACTIVE':
                break
            delete_chameleon_lease(name)
            print(f"lease['status'] = {lease['status']}, retrying...")
            time.sleep(interval)
            
        else:
            break
    
    return lease



