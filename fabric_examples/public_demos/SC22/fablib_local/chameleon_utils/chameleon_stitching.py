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

# FABRIC Library
from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager

BLAZAR_TIME_FORMAT = '%Y-%m-%d %H:%M'


def create_chameleon_fabnetv4_network(name='fabric_chameleon_stitch', 
                                      add_chameleon_router=False, 
                                      os_username=None, 
                                      os_password=None, 
                                      os_project_id=None, 
                                      lease=None):
    import os

    if os_project_id != None:
        os.environ["OS_PROJECT_ID"]=os_project_id  
        
    if os_password != None:
        os.environ["OS_PASSWORD"]=os_password
        
    if os_username != None:
        os.environ["OS_USERNAME"]=os_username
    
    print(f"Creating Chameleon lease and network {name} ...") 

    if lease == None:
        chameleon_lease = create_chameleon_stitched_network(name=name, stitch_provider='fabric') 
    else:
        chameleon_lease = lease
    
    print(f"Chameleon lease: {chameleon_lease['id']}") 
    
    chameleon_network = get_chameleon_network(chameleon_network_name=name, lease=chameleon_lease)
    chameleon_network_id = chameleon_network['id']
    network_vlan = chameleon_network['provider:segmentation_id']
    
    print(f"Chameleon network ready, ID: {chameleon_network_id}, vlan: {network_vlan}") 

    
    # Create a FABlib manager
    fablib = fablib_manager()
    
    print(f"Creating FABRIC slice...") 

    fabric_slice = create_fabric_slice(fablib=fablib, fabric_slice_name=name, vlan=network_vlan)
    fabric_network = get_fabric_network(fablib=fablib, fabric_slice_name=name)
    
    print(f"FABRIC slice ready, FABnet subnet: {fabric_network.get_subnet()}, gw: {fabric_network.get_gateway()}") 

        
    network_available_ips = fabric_network.get_available_ips()

    print(f"Configuring Chameleon network...")
    configure_chameleon_network(chameleon_network_name=name,
                                chameleon_network=chameleon_network, 
                                subnet=fabric_network.get_subnet(), 
                                chameleon_allocation_pool_start=network_available_ips[1], 
                                chameleon_allocation_pool_end=network_available_ips[250],
                                chameleon_gateway_ip=network_available_ips[0],
                                fabric_gateway=fabric_network.get_gateway(),
                                add_chameleon_router=add_chameleon_router)
    
    
    print(f"Chameleon FABnet stitch is ready")


def delete_chameleon_fabnet_stitch(name='fabric_chameleon_stitch', 
                                   delete_chameleon_router=False, 
                                   os_username=None, 
                                   os_password=None, 
                                   os_project_id=None):
    import os
    
    if os_project_id != None:
        os.environ["OS_PROJECT_ID"]=os_project_id  
        
    if os_password != None:
        os.environ["OS_PASSWORD"]=os_password
        
    if os_username != None:
        os.environ["OS_USERNAME"]=os_username
    
    import chi
    import chi.lease 
    
    print(f"Deleting Chameleon FABRIC stitch {name}")
    
    # Delete FABRIC slice
    print(f"Deleting the FABRIC slice...")
    try:
        # Create a FABlib manager
        fablib = fablib_manager()
        
        fabric_slice = fablib.delete_slice(slice_name=name)
    except Exception as e:
        print(f"Exception: {e}")
        
    try:
        print(f"Deleting the Chameleon Lease...")
        chi.lease.delete_lease(name)
    except Exception as e:
        print(f"Exception: {e}")   
    
    if delete_chameleon_router:
        try:
            # Delete the Router
            print(f"Deleting the Chameleon Router...")
            chi.network.delete_router(chi.network.get_router_id(name))
        except Exception as e:
            print(f"Exception: {e}")   
        
    print(f"Done")
    
def add_chameleon_l2network(name='fabric_chameleon_stitch', 
                                      add_chameleon_router=False, 
                                      os_username=None, 
                                      os_password=None, 
                                      os_project_id=None,
                                      fabric_slice=None, 
                                      lease=None):
    import os

    if os_project_id != None:
        os.environ["OS_PROJECT_ID"]=os_project_id  
        
    if os_password != None:
        os.environ["OS_PASSWORD"]=os_password
        
    if os_username != None:
        os.environ["OS_USERNAME"]=os_username
    
    print(f"Creating Chameleon lease and network {name} ...") 

    if lease == None:
        chameleon_lease = create_chameleon_stitched_network(name=name, stitch_provider='fabric') 
    else:
        chameleon_lease = lease
    
    print(f"Chameleon lease: {chameleon_lease['id']}") 
    
    chameleon_network = get_chameleon_network(chameleon_network_name=name, lease=chameleon_lease)
    network_vlan = get_chameleon_network_vlan(chameleon_network=chameleon_network)
    chameleon_network_id = get_chameleon_network_id(chameleon_network=chameleon_network)
    
    #chameleon_network_id = chameleon_network['id']
    #network_vlan = chameleon_network['provider:segmentation_id']
    
    print(f"Chameleon network ready, ID: {chameleon_network_id}, vlan: {network_vlan}") 

    
    # Create a FABlib manager
    #fablib = fablib_manager()
    
    print(f"Creating FABRIC slice...") 

    #fabric_slice = create_fabric_slice(fablib=fablib, fabric_slice_name=name, vlan=network_vlan)
    #fabric_network = get_fabric_network(fablib=fablib, fabric_slice_name=name)
    
    print(f"FABRIC slice ready, FABnet subnet: {fabric_network.get_subnet()}, gw: {fabric_network.get_gateway()}") 

        
    network_available_ips = fabric_network.get_available_ips()

    print(f"Configuring Chameleon network...")
    configure_chameleon_network(chameleon_network_name=name,
                                chameleon_network=chameleon_network, 
                                subnet=fabric_network.get_subnet(), 
                                chameleon_allocation_pool_start=network_available_ips[1], 
                                chameleon_allocation_pool_end=network_available_ips[250],
                                chameleon_gateway_ip=network_available_ips[0],
                                fabric_gateway=fabric_network.get_gateway(),
                                add_chameleon_router=add_chameleon_router)
    
    
    print(f"Chameleon FABnet stitch is ready")

        
def create_chameleon_stitched_network(name=None, stitch_provider='fabric'):
    import chi
    import chi.lease 
    
    lease_name=name
    network_name=name
     
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
    
    return lease

def get_chameleon_network_vlan(chameleon_network=None):
    return chameleon_network['provider:segmentation_id']
                            
def get_chameleon_network_id(chameleon_network=None):
    return chameleon_network['id']

def get_chameleon_network(chameleon_network_name=None, lease=None, retry=25, retry_interval=5):
    import chi
    import chi.lease 
    
    chameleon_network_reservation_id = [reservation for reservation in lease['reservations'] if reservation['resource_type'] == 'network'][0]['id']
    #print(f"chameleon_network_reservation_id: {chameleon_network_reservation_id}")
    
    network_vlan = None
    
    print("Waiting for Chameleon network ", end='')
    for attempt in range(retry):
       
        try:
            #Get the network
            chameleon_network = chi.network.get_network(chameleon_network_name)

            #Get the network ID
            chameleon_network_id = chameleon_network['id']
            #print(f'Chameleon Network ID: {chameleon_network_id}')

            #Get the VLAN tag (needed for FABRIC stitching)
            network_vlan = chameleon_network['provider:segmentation_id']
            #print(f'network_vlan: {network_vlan}')
        except Exception as e:
            if attempt+1 >= retry:
                print(" Failed")
                raise e

            #print(f"Exception: {e}")
            #traceback.print_exc()
            #print(f'Chameleon Network is not ready. Trying again!')
            print(".", end='')
            time.sleep(retry_interval)   
         
        if network_vlan != None:
            break
    print(" Done!")
    return chameleon_network

def create_fabric_slice(fablib=None, fabric_slice_name=None, vlan=None):
    try:
        #Create a slice
        fabric_slice = fablib.new_slice(name=fabric_slice_name)

        print(f"create_fabric_slice:  name {fabric_slice_name} vlan: {vlan}")

        fabric_facility_port = fabric_slice.add_facility_port(name='Chameleon-StarLight', site='STAR', vlan=str(vlan))
        fabric_facility_port_iface = fabric_facility_port.get_interfaces()[0]

        fabric_fabnet = fabric_slice.add_l3network(name=fabric_slice_name, interfaces=[fabric_facility_port_iface], type='IPv4')

        #Submit the Request
        fabric_slice.submit(progress=False)
        
        
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()
        
    return fabric_slice

def get_fabric_network(fablib=None, fabric_slice_name=None):
    try:
        #Create a slice
        fabric_slice = fablib.get_slice(name=fabric_slice_name)

        fabric_network = fabric_slice.get_network(name=fabric_slice_name)
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()
        
    return fabric_network

def configure_chameleon_network(chameleon_network_name=None,
                                chameleon_network=None, 
                                subnet=None, 
                                chameleon_allocation_pool_start=None, 
                                chameleon_allocation_pool_end=None,
                                chameleon_gateway_ip=None,
                                fabric_gateway=None,
                                add_chameleon_router=False,
                                fabric_route_subnet=None): 
    import chi
    import chi.lease 
    chameleon_subnet_name = chameleon_network_name
    chameleon_router_name = chameleon_network_name
    
    chameleon_subnet = chi.network.create_subnet(chameleon_subnet_name, chameleon_network['id'], 
                                                 cidr=str(subnet),
                                                 allocation_pool_start=chameleon_allocation_pool_start,
                                                 allocation_pool_end=chameleon_allocation_pool_end,
                                                 gateway_ip=chameleon_gateway_ip)
    
    
    if fabric_gateway and fabric_route_subnet:
        chi.neutron().update_subnet(subnet=chameleon_subnet['id'] ,
                                    body={
                                         "subnet": { 
                                             "host_routes": [ 
                                                    {
                                                        "destination": f"{fabric_route_subnet}", 
                                                         "nexthop": f"{fabric_gateway}"
                                                    }
                                             ] 
                                         }
                                    })

  


    if add_chameleon_router:
        #print(json.dumps(chameleon_subnet, indent=2))
        chameleon_router = chi.network.create_router(chameleon_router_name, gw_network_name='public')

        #print(json.dumps(chameleon_router, indent=2))
        chi.network.add_subnet_to_router_by_name(chameleon_router_name, chameleon_subnet_name)
    

