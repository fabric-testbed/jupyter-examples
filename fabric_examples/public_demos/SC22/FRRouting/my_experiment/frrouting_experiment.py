#!/bin/python3

import json
import time
from ipaddress import ip_address, IPv4Address, IPv6Address, IPv4Network, IPv6Network

from fabrictestbed_extensions.fablib.fablib import FablibManager as fablib_manager


import os
import sys

#module_path = os.path.abspath(os.path.join(f"{os.environ['HOME']}/work/PRUTH-FABRIC-Examples/fablib_local"))
module_path = os.path.abspath(os.path.join(f"../../fablib_local"))
if module_path not in sys.path:
    sys.path.append(module_path)
from fablib_custom.fablib_custom import *




from chameleon_utils.chameleon_stitching import *
from chameleon_utils.chameleon_servers import *

from fablib_common_utils.utils import *

from performance_testing.iperf3 import *



import os
import sys

import ipycytoscape as cy
from IPython.display import display
from ipywidgets import Output
import ipywidgets as widgets
from ipywidgets import HTML, Layout


#module_path = os.path.abspath(os.path.join('..'))
#if module_path not in sys.path:
#    sys.path.append(module_path)

from chameleon_utils.chameleon_stitching import *
from chameleon_utils.chameleon_servers import *
from fablib_common_utils.utils import *

from concurrent.futures import ThreadPoolExecutor


#from fablib_local_imports.common_notebook_utils.utils import *
#from fablib_local_imports.common_notebook_utils.fablib_plugin_methods import *
#from fablib_local_imports.common_notebook_utils.fabric_fabnet_slice import *

#from plugins import Plugins
#Plugins.load()

# Define Experiment
class FRRouting_Experiment():

    config = None
    
    fablib = None
    slice = None
    slice_id = None
    slice_name = None
    
    router_subnets = []
    local_subnets = []
    all_cidr = None           # 192.168.0.0/16
    all_ip = None             # 192.168.0.0
    all_backward_mask = None  # 0.0.255.255
    all_mask = None           # 255.255.0.0
     
    #router_names = []
    #router_links = []
    #local_networks = []
    
    nodes = []
    
    def __init__(self, 
                 name,
                 output=None,
                 node_tools=f"../fabric_node_tools",
                 config = None,
                 verbose=False):
        
        
        if verbose:
            print(f"Initializing FRRouting Slice: {name}")
            
            
        self.config = config
            
        self.fablib = fablib_manager(output=output)
        #self.fablib = fablib_manager()
        self.slice_name = name
        self.slice = self.fablib.new_slice(name=self.slice_name)
        self.slice_id = None
        
        #self.router_names = []
        #self.router_links = []
        #self.local_networks = []
        
        self.nodes = []
        
        # Default IP pools: TODO: allow custom IP pools
        self.all_cidr = '192.168.0.0/16'
        self.all_ip = '192.168.0.0'
        self.all_backward_mask = '0.0.255.255'
        self.all_mask = '255.255.0.0'
        
        #self.router_subnets = []
        #for i in range(1,33):
        #    self.router_subnets.append(IPv4Network(f"192.168.{200+i}.0/24"))
            
        #self.local_subnets = []
        #for i in range(1,33):
        #    self.local_subnets.append(IPv4Network(f"192.168.{i}.0/24"))
            
        self.thread_pool_executor = ThreadPoolExecutor(10)
        
    
    def configure(self):
        import traceback
        try:
            self.node_logs = {}
            
            # Add routers            
            iface_map = {}
            for network in self.config['networks']:
                #if network['facility'] == 'FABRIC':
                router = self.add_router(network)
                iface_name = f'{router.get_name()}-local-p1'
                iface_map[network['name']] = [ router.get_interface(name=iface_name) ]         
                
                if network['facility'] == 'CHI@UC':
                    network_lease_name = f"fabric_stitch3_{network['name']}"
                    
                    chameleon_subnet = IPv4Network(network['subnet'])
                    chameleon_allocation_pool_start = IPv4Address(network['allocation_pool_start'])
                    chameleon_allocation_pool_end = IPv4Address(network['allocation_pool_end'])
                    
                    if 'chameleon_gateway_ip' in network:
                        chameleon_gateway_ip = IPv4Address(network['chameleon_gateway_ip'])
                        add_chameleon_router = True
                    else:
                        chameleon_gateway_ip = None
                        add_chameleon_router = False
                    
                    fabric_gateway_ip = IPv4Address(network['router']['ip'])

                    # create chameleon network and add facility port
                    chameleon_net_lease = create_chameleon_stitched_network(name=network_lease_name)
        
                    chameleon_network = get_chameleon_network(chameleon_network_name=network_lease_name, lease=chameleon_net_lease)
                    stitch_vlan = get_chameleon_network_vlan(chameleon_network=chameleon_network)
                    chameleon_network_id = get_chameleon_network_id(chameleon_network=chameleon_network)

                    print(f"network_lease_name: {network_lease_name}")
                    print(f"stitch_vlan: {stitch_vlan}")
                    print(f"chameleon_network_id: {chameleon_network_id}")
                     
                    #chameleon_server_name = network_lease_name
                    chameleon_network_name = network_lease_name
                    chameleon_subnet_name = network_lease_name
                    chameleon_router_name = network_lease_name
    
                    configure_chameleon_network(chameleon_network_name=network_lease_name,
                                chameleon_network=chameleon_network, 
                                subnet=chameleon_subnet, 
                                chameleon_allocation_pool_start=chameleon_allocation_pool_start, 
                                chameleon_allocation_pool_end=chameleon_allocation_pool_end,
                                chameleon_gateway_ip=chameleon_gateway_ip,
                                fabric_gateway=fabric_gateway_ip,
                                add_chameleon_router=add_chameleon_router,
                                fabric_route_subnet="192.168.0.0/16")   
        
                    # Create fabric facility port
                    fabric_facility_port = self.slice.add_facility_port(name='Chameleon-StarLight', 
                                                                        site='STAR', 
                                                                        vlan=str(stitch_vlan))
                    fabric_facility_port_iface = fabric_facility_port.get_interfaces()[0]
                
                    iface_map[network['name']].append(fabric_facility_port_iface)

            # Add links between routers
            for link in self.config['links']:
                self.add_router_link(link)
            
            
            # Add local nodes
            for exp_node in self.config['nodes']:
                exp_network = list(filter(lambda x:x['name'] == exp_node['network'], self.config['networks']))[0]
                if exp_node['facility'] == 'FABRIC':
                    fim_node = self.slice.add_node(name=exp_node['name'], 
                                                   site=exp_network['site'],
                                                   cores=exp_node['cores'], 
                                                   ram=exp_node['ram'], 
                                                   disk=exp_node['disk'])
                    iface_map[exp_node['network']].append(fim_node.add_component(model='NIC_Basic', name='nic1').get_interfaces()[0])
                elif exp_node['facility'] == 'CHI@UC':
                    
                    pass


            # Add local networks and nodes
            for network,ifaces in iface_map.items():
                ex_network = self.get_ex_network(network)
                if ex_network['facility'] == 'CHI@UC':
                    self.slice.add_l2network(name=network, interfaces=ifaces, type='L2STS')
                else:
                    self.slice.add_l2network(name=network, interfaces=ifaces)
                
                
                
            
            
            self.submit()
            
        except Exception as e:
            print(f"Slice Fail: {e}")
            traceback.print_exc()
        
    def deploy(self):
        print('Submit FABRIC Slice...')
        #self.submit()
        print('Wait for all nodes...')
        #self.test_ssh()
        print('Deploy Node Tools...')
        self.execute_on_all_nodes(f'rm -rf fabric_node_tools')
        self.upload_directory_to_all_nodes('fabric_node_tools','.')
        self.execute_on_all_nodes(f'chmod +x fabric_node_tools/*.sh ; '
                                       f'sudo ./fabric_node_tools/host_config_redhat.sh; '
                                       f'sudo ./fabric_node_tools/host_tune_redhat.sh')
        print('Configure Node Devices...')
        self.configure_devs()
        print('Configure Routers...')
        self.configure_routers()
        #print('Tune Network Devices...')
        #command = f'sudo ./fabric_node_tools/host_tune_redhat.sh'
        #self.execute_on_all_edge_nodes(f'{command}')
        print('Done')

        
        

    
            
    def get_ssh_thread_pool_executor(self):
        return self.thread_pool_executor

    def list_sites(self):
        self.fablib.list_sites()               
        
    def __get_slice(self):
        return self.slice
    
    def __get_slice_name(self):
        return self.slice_name
    
    def __get_slice_id(self):
        return self.slice_id    
    
    def load(self, slice_name=None, path='config', verbose=False):
        #print(f"Loading Slice")# {slice_name}")
        
        file = open(f"{path}/{self.slice_name}_data.json", "r") 
        config_str = file.read()
        file.close() 
        
        self.config = json.loads(config_str)
        #self.slice_id = config['slice_id']
        #self.slice_name = config['slice_name']
        #self.router_names = config['router_names']
        #self.router_links = config['router_links']
        #self.local_networks = config['local_networks']
        #self.nodes = config['nodes']
        
        self.slice = self.fablib.get_slice(name=self.slice_name)
        #self.update_nodes()
        
        #if verbose:
        #    print(f"self.slice_id: {self.slice_id}")
        #    print(f"self.slice_name: {self.slice_name}")
        #    print(f"self.router_names: {self.router_names}")
        #    print(f"self.router_links: {self.router_links}")
        #    print(f"self.local_networks: {self.local_networks}")
        #    print(f"self.nodes: {self.nodes}")
        #    print(f"{self.slice}")
            
    
    def get_ex_network(self, network_name):
        return list(filter(lambda x: x['name'] == network_name, self.config['networks']))[0]
            
    def get_ex_router(self, network_name):
        return self.get_ex_network(network_name)['router']
    
    def get_ex_link(self, link_name):
        return list(filter(lambda x: x['name'] == link_name, self.config['links']))[0]
    
    def get_ex_node(self, node_name):
        return list(filter(lambda x: x['name'] == node_name, self.config['nodes']))[0]
    
        
    def get_fim_router(self, network_name):
        ex_router = self.get_ex_router(network_name)
        return self.slice.get_node(ex_router['name'])

    def add_router(self, network=None):
        
        ex_network = self.get_ex_network(network['name'])
        ex_router = self.get_ex_router(network['name'])
        
        router = self.slice.add_node(name=ex_router['name'], 
                                site=ex_router['site'], 
                                cores=ex_router['cores'], 
                                ram=ex_router['ram'], 
                                disk=ex_router['disk'], 
                                image='default_rocky_8')
        
        iface = router.add_component(model='NIC_Basic', name='local').get_interfaces()[0]
        #print(f"iface = {iface.get_name()}")
        
        return router
    
   
        
        
   
        
    def add_router_link(self, link=None):
    
        nic_model='NIC_Basic'
        
        link_name = link['name']
        subnet = link['subnet']
        endpoint1 = link['endpoints'][0]
        endpoint2 = link['endpoints'][1]
        
        
        fim_router1 = self.slice.get_node(name=endpoint1['router_name'])
        fim_router2 = self.slice.get_node(name=endpoint2['router_name'])

        if nic_model=='NIC_ConnectX_6':
            router1_iface1 = fim_router1.add_component(model='NIC_ConnectX_6', name=f'{link_name}').get_interfaces()[0]
            router2_iface1 = fim_router2.add_component(model='NIC_ConnectX_6', name=f'{link_name}').get_interfaces()[0]
        elif nic_model=='NIC_ConnectX_5':
            router1_iface1 = fim_router1.add_component(model='NIC_ConnectX_5', name=f'{link_name}').get_interfaces()[0]
            router2_iface1 = fim_router2.add_component(model='NIC_ConnectX_5', name=f'{link_name}').get_interfaces()[0]
        else:
            router1_iface1 = fim_router1.add_component(model='NIC_Basic', name=f'{link_name}').get_interfaces()[0]
            router2_iface1 = fim_router2.add_component(model='NIC_Basic', name=f'{link_name}').get_interfaces()[0]
        
        #Create Router Links
        router_link = self.slice.add_l2network(name=link_name, interfaces=[router1_iface1, router2_iface1])
                
        return router_link

    def add_chameleon_local_network(self, name=None, router=None, subnet=None, 
                                       router_ip=None, node_count=0, verbose=False):
     
            
        
        # Create Chameleon leases
        time_stamp = datetime.now(tz=tz.tzutc()).strftime('%Y%m%d%H%M')

        network_lease_name = f"pruth_{time_stamp}_{name}_stitched_network"
        server_lease_name = f"pruth_{time_stamp}_{name}_stitched_servers"
        #server_lease_name = f"{name}"
        
        ifaces = []
        
        router = self.slice.get_node(name=router.get_name())
        router_iface = router.add_component(model='NIC_ConnectX_6', name=f'{name}').get_interfaces()[0]
        #router_iface = router.add_component(model='NIC_Basic', name=f'{name}').get_interfaces()[0]
        
        ifaces.append(router_iface)
            
        site = router.get_site()
        
        #Create Chameleon network
        fabric_net_lease = create_chameleon_stitched_network(name=network_lease_name)
        
        chameleon_network = get_chameleon_network(chameleon_network_name=network_lease_name, lease=fabric_net_lease)
        stitch_vlan = get_chameleon_network_vlan(chameleon_network=chameleon_network)
        chameleon_network_id = get_chameleon_network_id(chameleon_network=chameleon_network)
        
        if verbose:
            print(f"network_lease_name: {network_lease_name}")
            print(f"stitch_vlan: {stitch_vlan}")
            print(f"chameleon_network_id: {chameleon_network_id}")
        
        
        #chameleon_server_name = network_lease_name
        chameleon_network_name = network_lease_name
        chameleon_subnet_name = network_lease_name
        chameleon_router_name = network_lease_name
        
        #Network Config
        #subnet = IPv4Network("192.168.100.0/24")
        
        chameleon_gateway_ip=local_network_available_ips[10]
        router_ip=local_network_available_ips[11]
        chameleon_allocation_pool_start=local_network_available_ips[12]
        chameleon_allocation_pool_end=local_network_available_ips[43]    
        local_network_available_ips = local_network_available_ips[44:] 
        
        if verbose:
            print(f"chameleon_gateway_ip: {chameleon_gateway_ip}")
            print(f"router_ip: {router_ip}")
            print(f"chameleon_allocation_pool_start: {chameleon_allocation_pool_start}")
            print(f"chameleon_allocation_pool_end: {chameleon_allocation_pool_end}")
                
        configure_chameleon_network(chameleon_network_name=network_lease_name,
                                chameleon_network=chameleon_network, 
                                subnet=local_network_subnet, 
                                chameleon_allocation_pool_start=chameleon_allocation_pool_start, 
                                chameleon_allocation_pool_end=chameleon_allocation_pool_end,
                                chameleon_gateway_ip=chameleon_gateway_ip,
                                fabric_gateway=router_ip,
                                add_chameleon_router=True,
                                fabric_route_subnet="192.168.0.0/16")    
        
        
        fabric_facility_port = self.slice.add_facility_port(name='Chameleon-StarLight', site='STAR', vlan=str(stitch_vlan))
        fabric_facility_port_iface = fabric_facility_port.get_interfaces()[0]

        fabric_net = self.slice.add_l2network(name=f'{name}', 
                                              interfaces=[router_iface,fabric_facility_port_iface]) 
    
        nodes = []
        if node_count > 0:
            server_lease = create_chameleon_server_lease(name=server_lease_name, count=node_count) 
            
            for i in range(1,node_count+1):
                #node_name = f"{server_lease_name}{i}"
                node_name = f"{name}{i}"
                create_chameleon_servers(name=node_name, 
                                  count=1, 
                                  #node_type=default_chameleon_node_type,
                                  #image_name=default_chameleon_image_name,
                                  key_name='my_chameleon_key',
                                  network_name=chameleon_network_name,
                                  lease=server_lease)
                
                server_id = chi.server.get_server_id(node_name)
                fixed_ip = chi.server.get_server(server_id).interface_list()[0].to_dict()["fixed_ips"][0]["ip_address"]
                
                floating_ip=get_free_floating_ip()
                floating_ip_address = floating_ip['floating_ip_address']
    
                associate_floating_ip(server_id, floating_ip_address=floating_ip_address)
                
                self.nodes.append( { 'name': node_name,
                                     'facility': 'CHI@UC',
                                     'site': 'CHI@UC',
                                     'management_ip': str(floating_ip_address),
                                     'data_plane_ip': str(fixed_ip),
                                     'local_net': str(name),
                                   } 
                                 )
                
                

         
        local_network_info = {  'name': name,
                                'router_site': site,
                                'node_site': 'Chameleon@UC',                                
                                'subnet': str(local_network_subnet),
                                'router': {'name': router.get_name(), 'ip': str(router_ip) },
                                'nodes' : nodes 
                                }
        
        self.local_networks.append(local_network_info)
        
        self.save_config()
            
        
    
    def add_local_network(self, name=None, 
                                       router=None, 
                                       subnet=None, 
                                       router_ip=None, 
                                       node_count=1,
                                       cores=2, ram=8, disk=10, image='default_rocky_8'):
         # Organize the subnets and IPs
        if subnet:
            local_network_subnet = subnet
        else:
            local_network_subnet = self.get_available_local_subnet() #IPv4Network("192.168.101.0/24")
            
        local_network_available_ips = list(local_network_subnet)[1:]
        
        if not router_ip:
            router_ip = local_network_available_ips.pop(0)
              
        ifaces = []
        
        router = self.slice.get_node(name=router.get_name())
        router_iface = router.add_component(model='NIC_Basic', name=f'{name}').get_interfaces()[0]
        
        ifaces.append(router_iface)
            
        site = router.get_site()
        nodes = []
        for i in range(node_count):
            node_name=f'{name}{i+1}'
            self.node_logs[node_name] = f'{node_name}.log'

            
            node = self.slice.add_node(name=node_name, site=site, cores=cores, ram=ram, disk=disk, image=image)
            node_iface = node.add_component(model='NIC_Basic', name=f'{name}').get_interfaces()[0]
            ifaces.append(node_iface)
            node_ip = local_network_available_ips.pop(0)
            nodes.append({'name': node_name, 'ip': str(node_ip)})
            
            self.nodes.append( { 'name': node_name,
                                 'facility': 'FABRIC',
                                 'site': site,
                                 'management_ip': None,
                                 'data_plane_ip': str(node_ip),
                                 'local_net': str(name),
                                   } 
                                 )
        
        router_local_network = self.slice.add_l2network(name=name, interfaces=ifaces)
 
        local_network_info = {  'name': name,
                                'router_site': site,
                                'node_site': site,
                                'subnet': str(local_network_subnet),
                                'router': {'name': router.get_name(), 'ip': str(router_ip) },
                                'nodes' : nodes 
                                }
        
        self.local_networks.append(local_network_info)
        
        self.save_config()

        
        return router_local_network
    

    def get_all_network_ex_nodes(self, network_name):
        
        ex_nodes = list(filter(lambda x:x['network'] == network_name, self.config['nodes']))
        
        ex_network = self.get_ex_network(network_name)
        ex_nodes.append(ex_network['router'])
                                   
        return ex_nodes
                        
   
    def configure_devs(self, verbose=False):
        
        # Configure router links
        for ex_link in self.config['links']:
            link_name =   ex_link['name']
            link_subnet = IPv4Network(ex_link['subnet'])
            
            if verbose:
                print(f"Config: {link_name}, {link_subnet}")
                
            endpoint1 = ex_link['endpoints'][0]
            endpoint2 = ex_link['endpoints'][1]
            
            fim_router1 = self.slice.get_node(endpoint1['router_name'])
            router1_ip = IPv4Address(endpoint1['ip'])
            router1_iface = fim_router1.get_interface(network_name=link_name)
            #router1_dev = router1_iface.get_os_interface()
            router1_iface.ip_addr_add(addr=router1_ip, subnet=link_subnet)
            
            fim_router2 = self.slice.get_node(endpoint2['router_name'])
            router2_ip = IPv4Address(endpoint2['ip'])
            router2_iface = fim_router2.get_interface(network_name=link_name)
            #router2_dev = router2_iface.get_os_interface()
            router2_iface.ip_addr_add(addr=router2_ip, subnet=link_subnet)

        # Configure local networks
        for local_network in self.config['networks']: 
            
            
            local_network_name = local_network['name']
            local_network_subnet = IPv4Network(local_network['subnet'])
            local_network_router = self.slice.get_node(local_network['router']['name'])
            local_network_router_ip = IPv4Address(local_network['router']['ip'])
            local_network_router_iface = local_network_router.get_interface(network_name=local_network_name)

            local_network_router_iface.ip_addr_add(addr=local_network_router_ip, subnet=local_network_subnet) 
            
            if local_network['facility'] == 'CHI@UC':
                continue
            
            for ex_node in self.get_all_network_ex_nodes(local_network['name']):
                node_ip=IPv4Address(ex_node['ip'])
                node = self.slice.get_node(ex_node['name'])
                node_iface = node.get_interface(network_name=local_network['name'])
                #node_dev = node_iface.get_os_interface()
                print(f"ip_addr_add:  ip: {node_ip}, subnet:{IPv4Network(local_network['subnet'])}")
                node_iface.ip_addr_add(addr=node_ip, subnet=IPv4Network(local_network['subnet'])) 
                
                #for subnet in self.get_all_subnets():
                #    node.ip_route_add(subnet, local_network_router_ip)
                for static_route_subnet,static_route_gw in ex_node['static_routes']:
                    print(f"ip_route_add:  subnet: {IPv4Network(static_route_subnet)}, gw: {static_route_gw}")

                    node.ip_route_add(IPv4Network(static_route_subnet), static_route_gw)
                    
    #def get_routers(self):
    #    routers = []
    #    for router_name in self.router_names:  
    #        routers.append(self.slice.get_node(router_name))
    #    return routers
    
    
    def upload_directory(self, node, directory, verbose=False):
        #if verbose:
        #    print(json.dumps(node, indent=4))

        if node['facility'] == 'FABRIC':
            fnode = self.slice.get_node(node['name'])
            rtn_val = fnode.upload_directory(directory,'.')
            #if verbose:
            #    print(f"rtn_val: {rtn_val}")

        elif node['facility'] == 'CHI@UC':        
            rtn_val = upload_directory(directory,'.', 
                    username='cc', 
                    ip_addr= node['management_ip'],
                    private_key_file='/home/fabric/work/fablib_local_private_config/my_chameleon_key') 
            #if verbose:
            #    print(f"rtn_val: {rtn_val}")
        else:
            pass
            #if verbose:
            #    print('Unkown facility')
    
    def upload_file(self, node, local_file=None, remote_file='.', verbose=False):
        if verbose:
                print(json.dumps(node, indent=4))

        if node['facility'] == 'FABRIC':

            fnode = self.slice.get_node(node['name'])
            rtn_val = fnode.upload_file(local_file, remote_file)
            if verbose:
                print(f"rtn_val: {rtn_val}")

        elif node['facility'] == 'CHI@UC':        
            rtn_val = upload_file(local_file, remote_file, 
                    username='cc', 
                    ip_addr= node['management_ip'],
                    private_key_file='/home/fabric/work/fablib_local_private_config/my_chameleon_key') 
            if verbose:
                print(f"rtn_val: {rtn_val}")
        else:
            if verbose:
                print('Unkown facility')
                
    def download_file(self, node, local_file=None, remote_file=None, verbose=False):
        if verbose:
                print(json.dumps(node, indent=4))

        if node['facility'] == 'FABRIC':

            fnode = self.slice.get_node(node['name'])
            rtn_val = fnode.download_file(local_file, remote_file)
            if verbose:
                print(f"rtn_val: {rtn_val}")

        elif node['facility'] == 'CHI@UC':        
            rtn_val = download_file(local_file, remote_file, 
                    username='cc', 
                    ip_addr= node['management_ip'],
                    private_key_file='/home/fabric/work/fablib_local_private_config/my_chameleon_key') 
            if verbose:
                print(f"rtn_val: {rtn_val}")
        else:
            if verbose:
                print('Unkown facility')
        
    def upload_directory_to_all_nodes(self, directory, verbose=False):
        threads = []
        for node in self.config['nodes']:            
            threads.append(self.get_ssh_thread_pool_executor().submit(self.upload_directory,
                                                            node,
                                                            directory,
                                                            verbose=False))
            
            
        for router in self.get_all_ex_routers():
            threads.append(self.get_ssh_thread_pool_executor().submit(self.upload_directory,
                                                            router,
                                                            directory,
                                                            verbose=False))
                        
            
            
            
        
        
       
            
                                                                       
        for t in threads:
            result = t.result()
            #print(f"{result}")
            
    def upload_directory_to_all_edge_nodes(self, directory, verbose=False):
        threads = []
        for node in self.nodes:
            threads.append(self.get_ssh_thread_pool_executor().submit(self.upload_directory,
                                                            node,
                                                            directory,
                                                            verbose=False))
                                                                       
        for t in threads:
            result = t.result()
            #print(f"{result}")
            
    
    
    def execute_chameleon_node(self, command, username='cc', ip_addr=None, private_key_file=None):
        pass
    
    
    def execute(self, node, command, verbose=False):
        stdout = None
        stderr = None
        
        if verbose:
                print(json.dumps(node, indent=4))

        if node['facility'] == 'FABRIC':
            fnode = self.slice.get_node(node['name'])
            stdout, stderr = fnode.execute(command, quiet=True, output_file=f'logs/{fnode.get_name()}.log')
            if verbose:
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")

        elif node['facility'] == 'CHI@UC':        
            stdout, stderr = execute(command, 
                    username='cc', 
                    ip_addr= node['management_ip'],
                    private_key_file='/home/fabric/work/fablib_local_private_config/my_chameleon_key') 
            if verbose:
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")
        else:
            if verbose:
                print('Unkown facility')
                
        return stdout,stderr

    def execute_thread(self, node, command, verbose=False): 
         return self.get_ssh_thread_pool_executor().submit(self.execute,
                                                            node,
                                                            command,
                                                            verbose=False)
        
    def get_all_ex_routers(self):
        routers = []
        for network in self.config['networks']:
            routers.append(network['router'])
              
        return routers
    
    def test_ssh(self):
        import time
        count = 1
        while True:
            try:
                self.execute_on_all_nodes('echo Hello, FABRIC from node `hostname -s`');
            except Exception as e:
                print(f"test_ssh failed, retrying! {count}")
                count += 1
                time.sleep(20)
    
    
    def execute_on_all_nodes(self, command, verbose=False):
        threads = []
        for node in self.config['nodes']:
            threads.append(self.execute_thread(node,command,verbose=verbose))
            
            
        for router in self.get_all_ex_routers():
            threads.append(self.execute_thread(router,command,verbose=verbose))
            
        #for network in self.config['networks']:
        #    log_file = f"logs/{network['gw_name']}.log"
        #    router = self.slice.get_node(network['gw_name'])
        #    threads.append(router.execute_thread(command, output_file=log_file))
            
        for t in threads:
            stdout, stderr = t.result()
    
    def execute_on_all_edge_nodes(self, command, verbose=False):
        
        threads = []
        for node in self.config['nodes']:
            threads.append(self.execute_thread(node,command,verbose=verbose))
            
        for t in threads:
            stdout, stderr = t.result()
            
            
    def get_node(self, name):
        for node in self.nodes:
            if node['name'] == name:
                return node
            
        return None
                
            
    def get_edge_nodes(self):
        edge_nodes = []
        
        for node in self.nodes:
            if not node.get_name() in self.router_names:
                edge_nodes.append(node)
        return edge_nodes
    
    def get_local_networks(self):        
        return self.local_networks
    
    def get_local_network(self,name): 
        for net in self.get_local_networks():
            if net['name'] == name:
                return net
        
        return None
    
    #def get_local_network_names(self): 
    #    local_network_names = []
    #    for net in self.get_local_networks():
    #        local_network_names.append(net['name'])
    #    
    #    return local_network_names
    
    def get_router_links(self):        
        return self.router_links

    def get_router_link(self,name): 
        for link in self.get_router_links():
            if link['name'] == name:
                return link
        
        return None
    
    def get_router_link_names(self):
        router_link_names = []
        for link in self.get_router_links():
            router_link_names.append(link['name'])
        
        return router_link_names
          
        
    def get_local_network_names(self):
        return list(map(lambda x: x['name'], self.config['networks']))
        
    def get_link_network_names(self):
        return list(map(lambda x: x['name'], self.config['links']))
    
    

    
    def configure_router(self, network=None, type='ospf', verbose=False):
        if verbose:
            print(f"config router: {network['name']}")
            
        ex_router = network['router']
        fim_router = self.get_fim_router(network['name'])
        
        log_file = f"logs/{fim_router.get_name()}.log"

        #router.upload_directory('fabric_node_tools','.')
        #router.execute(f'chmod +x fabric_node_tools/*.sh', quiet=True, output_file=log_file)

        #sudo ./node_utils/frr_config.sh  1.2.3.4 1.2.0.0/16 1.2.0.0 0.0.255.255 eth1:1.2.100.100/24 eth2:1.2.101.102/24 1.2.102.102/24


        zebra_devs = ''
        for iface in fim_router.get_interfaces():

            # Test if iface has a network. If not, skip this iface
            try:
                network_name = iface.get_network().get_name()
            except:
                continue

            if iface.get_network().get_name() in self.get_local_network_names():
                #local_network_name = iface.get_network().get_name()
                #local_network = self.get_local_network(local_network_name)
                router_local_ip = iface.get_ip_addr()
                
                ex_network = self.get_ex_network(iface.get_network().get_name())

                cidr=ex_network['subnet'].split('/')[1]
                ip=router_local_ip
                zebra_subnet=f"{ip}/{cidr}"
                print(f"network zebra_subnet = {zebra_subnet}")
                
                zebra_devs=f"{zebra_devs} {iface.get_os_interface()}:{zebra_subnet}"

            elif iface.get_network().get_name() in self.get_link_network_names():
                ex_link = self.get_ex_link(iface.get_network().get_name())
                
                cidr=ex_link['subnet'].split('/')[1]
                ip=iface.get_ip_addr()
                zebra_subnet=f"{ip}/{cidr}"
                print(f"link zebra_subnet = {zebra_subnet}")
                
                zebra_devs=f"{zebra_devs} {iface.get_os_interface()}:{zebra_subnet}"
            else:
                print(f"Found unknown network: {iface.get_network().get_name()}")


        command= 'sudo ./fabric_node_tools/frr_config.sh {} {} {} {} {}'.format(router_local_ip,
                                                                          self.all_cidr,
                                                                          self.all_ip,
                                                                          self.all_backward_mask,
                                                                          zebra_devs)
        #command=f'{command} {router_local_ip}'
        #command=f'{command} {self.all_cidr}'
        #command=f'{command} {self.all_ip}'
        #command=f'{command} {self.all_backward_mask}'
        #for all devs:   command=f'{command} dev:subnet_cidr'
        if verbose:
            print(f"router: {fim_router.get_name()}, command: {command}")

        return fim_router.execute(command, quiet=True, output_file=log_file)
    
    def configure_routers(self, type='ospf', verbose=False):
        threads = {}
        for network in self.config['networks']:
            print(f"Config router for network: {network['name']}")
            threads[network['name']] = self.get_ssh_thread_pool_executor().submit(self.configure_router,
                                                            network,
                                                            type=type)
            
        for network,t in threads.items():
            print(f"waiting for {network} config")
            stdout, stderr = t.result()
        
            if verbose:
                print(f"stdout: {stdout}")
                print(f"stderr: {stderr}")

       
    def save_config(self, path='config'):
    
        config = self.config
 
    
        file = open(f"{path}/{self.slice_name}_data.json", "w") 
        n = file.write(json.dumps(config))
        file.close() 
        
    
        
        
        
    def save_fim_topology(self, path='config'):
        self.slice.save(f"{path}/{self.slice_name}_topology.json")

    def configure_local_nodes(self):
        pass
    
    def create_chameleon_server(self, ex_node):
        
        
        node_name = f"{ex_node['name']}"
        compute_reservation_id = ex_node['compute_reservation_id']
        network_name = f"fabric_stitch3_{ex_node['network']}" 
        
        print(f"compute_reservation_id: {compute_reservation_id}")
        create_chameleon_servers(name=node_name, 
                          count=1, 
                          #node_type=default_chameleon_node_type,
                          #image_name=default_chameleon_image_name,
                          key_name='my_chameleon_key',
                          network_name=network_name,
                          compute_reservation_id=compute_reservation_id)

        server_id = chi.server.get_server_id(node_name)
        fixed_ip = chi.server.get_server(server_id).interface_list()[0].to_dict()["fixed_ips"][0]["ip_address"]

        floating_ip=get_free_floating_ip()
        floating_ip_address = floating_ip['floating_ip_address']

        associate_floating_ip(server_id, floating_ip_address=floating_ip_address)
        
        
        ex_node['management_ip'] = str(floating_ip_address)
        ex_node['ip'] = str(fixed_ip)
        
            
    def submit(self):
        
        for node in self.config['nodes']:
            if node['facility'] == 'CHI@UC':
                self.create_chameleon_server(node)
        
        #self.slice_id = self.slice.submit(wait=False)
        self.slice_id = self.slice.submit(wait_timeout=10000)
        
        self.save_config()
        
    def wait(self):
        self.slice.wait_ssh(progress=True)
        
    def wait_jupyter(self, timeout=600, interval=10):
        self.slice.wait_jupyter(timeout=timeout, interval=interval)
        
    def post_boot_config(self):
        self.slice.post_boot_config()
        
   

    def delete(self,name=None):
        fablib = fablib_manager()
        fablib.delete_slice(name)
        
    def iperf3_process_output(self,output_dir='output', verbose=False):

        files = os.listdir(output_dir)   

        run_suffix = '_client_summary_output' 
        runs = {}                
        for file in files:
            if file.endswith(run_suffix):
                run_name = file.removesuffix(run_suffix)

                #open text file in read mode
                #print(f"file: {output_dir}/{file}")
                f = open(f'{output_dir}/{file}', "r")
                run_output = f.read()
                f.close()

                runs[run_name] =  json.loads(run_output)


        #print(f"{runs}")
        table = []
        for run_name,streams in runs.items():

            #print(f"{run_name}")

            run_bandwidth = 0.0
            run_retransmits = 0
            run_max_rtt = 0
            run_min_rtt = -1
            run_mean_rtt = 0
            run_mtu = 0

            for stream in streams:

                #for k1,v1 in stream.items():
                #    print(f"key: {k1}")

                run_mtu = stream['intervals'][0]['streams'][0]['pmtu']

                stream_port = stream['start']['connecting_to']['port']
                stream_bandwidth =  stream['end']['sum_received']['bits_per_second']*0.000000001
                stream_retransmits =  stream['end']['sum_sent']['retransmits']
                stream_max_rtt =  stream['end']['streams'][0]['sender']['max_rtt']*0.001
                stream_min_rtt =  stream['end']['streams'][0]['sender']['min_rtt']*0.001
                stream_mean_rtt =  stream['end']['streams'][0]['sender']['mean_rtt']*0.001
                stream_host_total = stream['end']['cpu_utilization_percent']['host_total']   
                stream_host_user = stream['end']['cpu_utilization_percent']['host_user']
                stream_host_system = stream['end']['cpu_utilization_percent']['host_system']
                stream_remote_total = stream['end']['cpu_utilization_percent']['remote_total']
                stream_remote_user = stream['end']['cpu_utilization_percent']['remote_user']
                stream_remote_system = stream['end']['cpu_utilization_percent']['remote_system']
                stream_sender_tcp_congestion = stream['end']['sender_tcp_congestion']
                stream_receiver_tcp_congestion = stream['end']['receiver_tcp_congestion']

                #print(f"Stream: {stream_port}. bw = {stream_bandwidth}")
                run_bandwidth += stream_bandwidth
                run_retransmits += stream_retransmits

                if stream_max_rtt > run_max_rtt:
                    run_max_rtt = stream_max_rtt

                if stream_min_rtt < run_min_rtt or run_min_rtt == -1:
                    run_min_rtt = stream_min_rtt

                run_mean_rtt += stream_mean_rtt

            run_mean_rtt = run_mean_rtt / len(streams)

            
            timestamp,source,target = run_name.split('__')
            #run = len(table)


            table.append( [    timestamp, source, target,
                                len(streams),
                                run_mtu,
                                f'{run_bandwidth:.3f}',
                                f'{run_max_rtt:.2f}',
                                f'{run_min_rtt:.2f}',
                                f'{run_mean_rtt:.2f}',
                                run_retransmits,
                                ] )
            #if verbose:
                #print(f"{run_name}: pmtu: {run_mtu}, bw: {run_bandwidth:.3f} Gbps, rtt ms (max/min/mean): {run_max_rtt:.2f}/{run_min_rtt:.2f}/{run_mean_rtt:.2f} ms, retransmits: {run_retransmits}")
        headers=["Timestamp", "Source", "Target", "P", "pmtu",  "bw", "rtt_max", "rtt_min", "rtt_mean", "retransmits" ]
        printable_table = self.create_table_local(table, title=f'iPerf3 Results', properties={'text-align': 'left'}, headers=headers, index='Timestamp')
        display(printable_table)

        
    def iperf3_run(self, 
                   source_node=None, 
                   target_node=None, 
                   w=None, P=1, t=60, i=10, O=None, verbose=True):
        from IPython.display import clear_output
        from concurrent.futures import ThreadPoolExecutor
        
        print(f"Running: {source_node['name']} to {target_node['name']} (w:{w}, P:{P}, t:{t}, O:{O}, i:{i}) ...")
        
        thread_pool_executor = ThreadPoolExecutor(10)
        
        target_ip=target_node['ip']
        
        #run_name=f"{source_node['name']}_{target_node['name']}_{datetime.now(tz=tz.tzutc()).strftime('%Y%m%d%H%M')}"
        run_name=f"{datetime.now(tz=tz.tzutc()).strftime('%Y%m%d%H%M')}__{source_node['name']}__{target_node['name']}"
        
        #target_thread = target_node.execute_thread(f'./fabric_node_tools/iperf3_server.sh {run_name} {P}')
        
        
        command = f'./fabric_node_tools/iperf3_server.sh {run_name} {P}'
        #command = f'iperf -J -t {t} -i {i} -c {target_ip} -P {P}'
        #if verbose:
            #print(f"Running: {command}")
        
        target_thread = self.execute_thread(target_node,command, verbose=False) 

        # Make sure the target is running before the source starts
        time.sleep(10)

        #net_name = f"{target_node['site']}_net"

        retry = 3
        while retry > 0:
            command = f'./fabric_node_tools/iperf3_client.sh {run_name} {target_ip} {P} -t {t} -i {i}'
            #command = f'iperf -J -t {t} -i {i} -c {target_ip} -P {P}'
            if O != None:
                command = f'{command} -O {O}'

            if w != None:
                command = f'{command} -w {w}'
            
            if verbose:
                print(f"{command}")

            source_thread = self.execute_thread(source_node, command, verbose=False)

            if verbose:
                print(f"source_thread: {source_thread}")
            
            source_stdout, source_stderr = source_thread.result()

            if verbose:
                print(f"source_stdout: {source_stdout}")
                print(f"source_stderr: {source_stderr}")


            #if 'error' in json.loads(source_stdout).keys():
            #    print(f"{source_node.get_name()} -> {target_node.get_name()} {target_ip}: error: {json.loads(source_stdout)['error']}")
            #    retry = retry - 1
            #    time.sleep(5)
            #    continue

            break



        #print(f"source_stderr: {source_stderr}")

        # Start target thread
        target_stdout, target_stderr = target_thread.result()
        if verbose:
            print(f"target_stdout: {target_stdout}")
            print(f"target_stderr: {target_stderr}")

        time.sleep(10)

        self.download_file(source_node, f'./output/{run_name}_client_summary_output',f'{run_name}_client_summary_output')
        self.download_file(target_node, f'./output/{run_name}_server_summary_output',f'{run_name}_server_summary_output')

        #source_node.download_file(f'./output/{run_name}_client_summary_output',f'{run_name}_client_summary_output')
        #target_node.download_file(f'./output/{run_name}_server_summary_output',f'{run_name}_server_summary_output')
        
        #if verbose:
        print(f"Done!")
        
    ######## Cytoscape Methods #########
    
    
    # FABRIC design elements https://fabric-testbed.net/branding/style/
    FABRIC_PRIMARY = '#27aae1'
    FABRIC_PRIMARY_LIGHT = '#cde4ef'
    FABRIC_PRIMARY_DARK = '#078ac1'
    FABRIC_SECONDARY = '#f26522'
    FABRIC_SECONDARY_LIGHT = '#ff8542'
    FABRIC_SECONDARY_DARK = '#d24502'
    FABRIC_BLACK = '#231f20'
    FABRIC_DARK = '#433f40'
    FABRIC_GREY = '#666677'
    FABRIC_LIGHT = '#f3f3f9'
    FABRIC_WHITE = '#ffffff'
    FABRIC_LOGO = "fabric_logo.png"

    def display_init(self):
        """
        Constructor
        :return:
        """
        #super().__init__()
    
        self.out = Output()

        

    def display_set_style(self):

        self.cytoscapeobj.set_style([
                        {
                        'selector': 'node',
                        'css': {
                            'content': 'data(name)',
                            'color': 'white',
                            'text-outline-width': 2,
                            'text-outline-color': self.FABRIC_DARK,
                            'background-color': self.FABRIC_GREY,
                            'font-weight': 400,
                            'text-halign': 'right',
                            'text-valign': 'bottom',
                            'font-size': 12,
                            }
                        },
                        {
                        'selector': "node.router",
                        'css': {
                            'text-outline-color': self.FABRIC_SECONDARY_DARK,
                            'background-color': self.FABRIC_SECONDARY,
                            'shape': 'roundrectangle',
                            }
                        },
                        {
                        'selector': "node.local_net",
                        'css': {
                            'text-outline-color': self.FABRIC_DARK,
                            'background-color': self.FABRIC_GREY,
                            'shape': 'triangle'
                            }
                        },
                        {
                        'selector': 'node.edge_node',
                        'css': {
                            'text-outline-color': self.FABRIC_PRIMARY_DARK,
                            'background-color': self.FABRIC_PRIMARY,
                            'shape': 'roundrectangle',
                            }
                        },
                        {
                        'selector': "node.selected",
                        'css': {
                            #'background-color': self.FABRIC_PRIMARY_DARK,
                            #'background-blacken': '0.2',
                            'border-color': self.FABRIC_BLACK,
                            'border-width': 6,
                            'border-style': 'solid',
                            'text-outline-color': self.FABRIC_BLACK,
                            #'background-opacity': 0.5
                            #'shape': 'round-diamond',
                            }
                        },
                        
                        #{
                        #  'selector': ":selected",
                        #  'css': {
                        #    "background-color": "black",
                        #    "line-color": "black",
                        #    "target-arrow-color": "black",
                        #    "source-arrow-color": "black"
                        #  }
                        #}
                        
                        ])


    def build_data(self, verbose=False):
        cy_nodes = self.data['nodes']
        cy_edges = self.data['edges']

        # Build Site
        #print(f"{self.router_names}")

        for network in self.config['networks']:
            
            ex_router = self.get_ex_router(network['name'])
            
            router_name = ex_router['name']
            router = self.slice.get_node(name=router_name) 
            if verbose:
                print(f"router_name: {router_name}, index: {self.router_names.index(router_name)}")
            #cy_nodes.append({ 'classes': 'router', 'data': { 'id': str(self.router_names.index(router_name)), 'name': router_name, 'href': 'http://cytoscape.org' }, 'position': {}})
            cy_nodes.append({ 'classes': 'router unselected', 'data': { 'id': router_name, 'name': router_name, 'href': 'http://cytoscape.org' }, 'position': {}})

            
        #print(f"{self.router_links}")
        for link in self.config['links']: 
            #router_links:
            router1_name = link['endpoints'][0]['router_name']
            router2_name = link['endpoints'][1]['router_name']        
            cy_edges.append({'data': { 'source': router1_name, 'target': router2_name } , 'position': {} })
            
        
        for local_network in self.config['networks']:
            #print(f"local_network: {local_network}")
            cy_nodes.append({ 'classes': 'local_net', 'data': { 'id': local_network['name'], 'name': local_network['subnet'], 'href': 'http://cytoscape.org' }, 'position': {}})
            cy_edges.append({'data': { 'source': local_network['router']['name'], 'target': local_network['name'] } , 'position': {} })
        
        
        for node in self.config['nodes']:
            #print(f"node: {node}")
            cy_nodes.append({ 'classes': 'edge_node unselected', 'data': { 'id': node['name'], 'name': node['name'], 'href': 'http://cytoscape.org' }, 'position': {}})
            cy_edges.append({'data': { 'source': node['network'], 'target': node['name'] } , 'position': {} })
        

        self.cytoscapeobj.graph.add_graph_from_json(self.data)
        
        #print(f"building cytoscape_node_map")
        self.cytoscape_node_map = {}
        for node in self.cytoscapeobj.graph.nodes:
            #print(node.data['id'])
            self.cytoscape_node_map[node.data['id']] = node

        #print(f"self.cytoscape_node_map: {self.cytoscape_node_map}")
        
       
        return 
    
    def setup_interaction(self):
        #out = Output()
        self.cytoscapeobj.on('node', 'click', self.on_click)
        #self.cytoscapeobj.on('node', 'mouseover', self.on_mouseover)
        
        self.run_btn.on_click(callback=self.run_btn_callback)
        self.clear_btn.on_click(callback=self.clear_btn_callback)
        self.path_btn.on_click(callback=self.path_btn_callback)

        
    def get_node_site(self, node_name):
        return self.get_ex_network(self.get_ex_node(node_name)['network'])['site']        
        
    def redraw_node_info(self):
        #with self.out:
        #    print('redraw_node_info: ')
        
        #with self.out: print(f"self.selected_node1: {self.selected_node1}")
        #with self.out: print(f"self.selected_node2: {self.selected_node2}")

        if self.selected_node1:                     
            #node1 = self.get_node(self.selected_node1.data['name'])
            node1 = self.get_ex_node(self.selected_node1.data['name'])
            #fim_node = self.slice.get_node(node1['name'])
            
            #with self.out: print(f"node1: {node1}")
            
            self.node1_info['name'].value = node1['name']
            self.node1_info['facility'].value = node1['facility']
            self.node1_info['site'].value = self.get_node_site(node1['name'])
            self.node1_info['dataplane_ip'].value = node1['ip']

            #with self.out: print(f"node1_info: {self.node1_info}")
            
            
            if node1['facility'] == 'FABRIC':
                fnode = self.slice.get_node(node1['name'])   
                self.node1_info['type'].value = f"VM (cores:{fnode.get_cores()}, ram: {fnode.get_ram()}, disk: {fnode.get_disk()})"
                self.node1_info['management_ip'].value = str(fnode.get_management_ip())

            elif node1['facility'] == 'CHI@UC': 
                self.node1_info['type'].value = 'Baremetal'
                self.node1_info['management_ip'].value = node1['management_ip']

            else:
                self.node1_info['type'].value = 'unknown'
        else:
            self.node1_info['name'].value = ''
            self.node1_info['type'].value = ''
            self.node1_info['site'].value = ''
            self.node1_info['facility'].value = ''            
            self.node1_info['dataplane_ip'].value = ''            
            self.node1_info['management_ip'].value = ''            
            
            
        if self.selected_node2:
            #node2 = self.get_node(self.selected_node2.data['name'])
            node2 = self.get_ex_node(self.selected_node2.data['name'])
            #fim_node = self.slice.get_node(node2['name'])
            
            #with self.out: print(f"node2: {node2}")
            
            self.node2_info['name'].value = node2['name']
            self.node2_info['facility'].value = node2['facility']
            self.node2_info['site'].value = self.get_node_site(node2['name'])
            self.node2_info['dataplane_ip'].value = node2['ip']

            #with self.out: print(f"node2_info: {self.node2_info}")
            
            
            if node2['facility'] == 'FABRIC':
                fnode = self.slice.get_node(node2['name'])   
                self.node2_info['type'].value = f"VM (cores:{fnode.get_cores()}, ram: {fnode.get_ram()}, disk: {fnode.get_disk()})"
                self.node2_info['management_ip'].value = str(fnode.get_management_ip())

            elif node2['facility'] == 'CHI@UC': 
                self.node2_info['type'].value = 'Baremetal'
                self.node1_info['management_ip'].value = node1['management_ip']

            else:
                self.node2_info['type'].value = 'unknown'
        else:
            self.node2_info['name'].value = ''
            self.node2_info['type'].value = ''
            self.node2_info['site'].value = ''
            self.node2_info['facility'].value = ''            
            self.node2_info['dataplane_ip'].value = ''            
            self.node2_info['management_ip'].value = ''  
            
            
        from IPython.display import clear_output
        from performance_testing.iperf3 import iperf3_process_output
        with self.out: 
            clear_output(wait=True)
            self.iperf3_process_output(verbose=False)
            #iperf3_process_output(verbose=True)

            
       
            
               
    def on_click(self, event):
        #with self.out:
            #print('\nclick: {}'.format(str(event)))
            #for node in self.cytoscapeobj.graph.nodes:
            #    print(node.data['name'])
            
        #with self.out: print(f'self.cytoscape_node_map: {self.cytoscape_node_map}')
        
        try:
            curr_node = self.cytoscape_node_map[str(event['data']['id'])]
            #curr_node = self.cytoscapeobj.graph.nodes[int(event['data']['id'])]
        except Exception as e:
            with self.out:
                print(e)
        
        #with self.out: print(f'here0')
         
        current_node_classes = curr_node.classes
        
        #with self.out: print(f'here0.1')
        classes = set(curr_node.classes.split(" "))
        #with self.out: print(f'here0.2')
        if 'selected' in classes:
            with self.out: print(f'returning, already selected: current_node_classes: {current_node_classes}')
            return
            
        #with self.out:
        #    print(f'current_node_classes: {current_node_classes}')
                
        if self.selected_node1 == None:
            #with self.out: print(f'setting: selected_node1: {current_node_classes}')
            self.selected_node1 = curr_node
        elif self.selected_node2 == None:
            #with self.out: print(f'setting: selected_node2: {current_node_classes}')
            self.selected_node2 = curr_node
        else:
            pass
            #with self.out: print(f'return without setting: selected_node: {current_node_classes}')

            return
        
        for node in self.cytoscapeobj.graph.nodes:
            classes = set(node.classes.split(" "))
            #print(f"classes: {classes}")
            if "selected" in classes:
                classes.remove("selected")
            classes.add("unselected")
            node.classes = " ".join(classes)
     
        #with self.out: print(f'here1')
    
        if self.selected_node1: 
            classes = set(self.selected_node1.classes.split(" "))
            #print(f"classes: {classes}")
            if "uselected" in classes:
                classes.remove("uselected")
            classes.add("selected")
            self.selected_node1.classes = " ".join(classes)
        
        #with self.out: print(f'here2')

        if self.selected_node2: 

            classes = set(self.selected_node2.classes.split(" "))
            #print(f"classes: {classes}")
            if "unselected" in classes:
                classes.remove("unselected")
            classes.add("selected")
            self.selected_node2.classes = " ".join(classes)

        #with self.out: print(f'here3')

        #with self.out: print(f"selected_node1: {self.selected_node1}")
        #with self.out: print(f"selected_node2: {self.selected_node2}")
        
        ##curr_node.classes += ' selected'
        #classes = set(curr_node.classes.split(" "))
        #if "unselected" in classes:
        #    classes.remove("unselected")
        #classes.add("selected")
        #curr_node.classes = " ".join(classes)
        
        self.redraw_node_info()
            
            
    def on_mouseover(self, node):
        pass
        #with self.out:
        #    print('mouseovers: {}'.format(str(node)))
            
    def path_btn_callback(self, btn):
        #with self.out: print(f'path_btn_callback')

        #if self.selected_node1 == None or self.selected_node2 == None:
        #    with self.out: print(f'run_btn_callback: needs to select two nodes')
        
        
        #with self.out: 
        #    print(f"run_btn_callback: testing: {self.selected_node1.data['name']} -> {self.selected_node2.data['name']}")
            
            
        with self.out: self.find_path(source_node=self.get_node(self.selected_node1.data['name']), 
                        target_node=self.get_node(self.selected_node2.data['name']), verbose=False)
        
        self.redraw_node_info()
        
    def clear_btn_callback(self, btn):
        #with self.out: print(f'clear_btn_callback')

        for node in self.cytoscapeobj.graph.nodes:
            classes = set(node.classes.split(" "))
            #print(f"classes: {classes}")
            if "selected" in classes:
                classes.remove("selected")
            classes.add("unselected")
            node.classes = " ".join(classes)
     
        self.selected_node1 = None
        self.selected_node2 = None
        
        self.redraw_node_info()
        
    def run_btn_callback(self, btn):
        
        #if self.selected_node1 == None or self.selected_node2 == None:
        #    with self.out: print(f'run_btn_callback: needs to select two nodes')
        
        
        #with self.out: 
        #    print(f"run_btn_callback: testing: {self.selected_node1.data['name']} -> {self.selected_node2.data['name']}")
            
        t=f"{self.iperf3_params_info['P'].value}"
        i=f"{self.iperf3_params_info['i'].value}"      
        O=f"{self.iperf3_params_info['O'].value}"                                            
        w=f"{self.iperf3_params_info['w'].value}m"
        P=f"{self.iperf3_params_info['P'].value}"                                               
            
        
        with self.out: self.iperf3_run(source_node=self.get_ex_node(self.selected_node1.data['name']), 
                        target_node=self.get_ex_node(self.selected_node2.data['name']), 
                        w=w, P=P, t=t, i=i, O=O, verbose=False)
        
        from IPython.display import clear_output
        from performance_testing.iperf3 import iperf3_process_output

        with self.out: 
            clear_output(wait=True)
            self.iperf3_process_output(verbose=False)
            #iperf3_process_output(verbose=True)
            
            
        


    def display(self):
        #update the fabric management ips
        #self.update_nodes()
            
        
            
        self.selected_node1 = None
        self.selected_node2 = None
        self.cytoscape_node_map = {}
        
        self.out = Output()
    
        self.cytoscapeobj = cy.CytoscapeWidget(layout=Layout(width='70%'))
        self.data = { 'nodes': [], 'edges': [] }
        
        self.display_set_style()
        
        #node1 info (right_top), node2 info (right_middle)
        self.node1_info = { 
                             'name': widgets.Label(value=""),
                             'type': widgets.Label(value=""),
                             'facility': widgets.Label(value=""),
                             'dataplane_ip': widgets.Label(value=""),
                             'site': widgets.Label(value=""),
                             'management_ip': widgets.Label(value=""),
                           }
        self.node2_info = { 
                             'name': widgets.Label(value=""),
                             'type': widgets.Label(value=""),
                             'facility': widgets.Label(value=""),
                             'dataplane_ip': widgets.Label(value=""),
                             'site': widgets.Label(value=""),
                             'management_ip': widgets.Label(value=""),
                           }        
        
        
         
        
        
        self.node1_label = widgets.Label(value="select node1")
        self.node2_label = widgets.Label(value="select node2")
        
        self.node1_box = widgets.VBox([ HTML('<center><b>Source Node</b></center>'),
                                        widgets.HBox([widgets.Label(value="Name:"), self.node1_info['name']] ),
                                        widgets.HBox([widgets.Label(value="Facility:"), self.node1_info['facility']] ),
                                        widgets.HBox([widgets.Label(value="Site:"), self.node1_info['site']] ),
                                        widgets.HBox([widgets.Label(value="Dataplane IP:"), self.node1_info['dataplane_ip']] ),
                                        widgets.HBox([widgets.Label(value="Management IP:"), self.node1_info['management_ip']] ),
                                        widgets.HBox([widgets.Label(value="type:"), self.node1_info['type']] ),
                                      ]) 
        self.node2_box = widgets.VBox([ HTML('<center><b>Target Node</b></center>'),
                                        widgets.HBox([widgets.Label(value="Name:"), self.node2_info['name']] ),
                                        widgets.HBox([widgets.Label(value="Facility:"), self.node2_info['facility']] ),
                                        widgets.HBox([widgets.Label(value="Site:"), self.node2_info['site']] ),
                                        widgets.HBox([widgets.Label(value="Dataplane IP:"), self.node2_info['dataplane_ip']] ),
                                        widgets.HBox([widgets.Label(value="Management IP:"), self.node2_info['management_ip']] ),
                                        widgets.HBox([widgets.Label(value="Type:"), self.node2_info['type']] ),
                                      ]) 
 
        self.iperf3_params_info = { 
                             'P': widgets.IntText(value=1,description='P:', disabled=False),
                             'i': widgets.IntText(value=1,description='i:', disabled=False),
                             't': widgets.IntText(value=20,description='t:', disabled=False),
                             'O': widgets.IntText(value=10,description='O:', disabled=False),
                             'w': widgets.IntText(value=16,description='w(m):', disabled=False),
                           }        
        

        self.iperf3_params_box = widgets.VBox([ HTML('<center><b>iPerf3 Parameters</b></center>'),
                                        self.iperf3_params_info['t'],
                                        self.iperf3_params_info['i'],
                                        self.iperf3_params_info['O'],
                                        self.iperf3_params_info['w'],
                                        self.iperf3_params_info['P'],
                                      ]) 
        
    
        #controls (right_bottom)
        self.path_btn = widgets.Button(description="Find Path", disabled=False)
        self.clear_btn = widgets.Button(description="Clear", disabled=False)
        self.run_btn = widgets.Button(description="Run iPerf", disabled=False)
        self.button_hbox = widgets.HBox( [self.path_btn, self.run_btn, self.clear_btn] )

        #right
        self.right_vbox = widgets.VBox( [HTML('<center><b><hr></b></center>'), 
                                         self.node1_box, 
                                         HTML('<center><b><hr></b></center>'), 
                                         self.node2_box, 
                                         HTML('<center><b><hr></b></center>'),
                                         self.iperf3_params_box,
                                         HTML('<center><b><hr></b></center>'),
                                         self.button_hbox  ,
                                         HTML('<center><b><hr></b></center>'),
                                         self.out] )
        
        
        #top
        self.top_hbox = widgets.HBox( [self.cytoscapeobj, self.right_vbox], width='100%', min_height='300px', overflow_y='hidden')       
        

                                            

        #main vbox
        self.main_vbox = widgets.VBox( [ self.top_hbox ] )
        
        
        self.setup_interaction()
        self.build_data()
    
        
        display(self.main_vbox)
        #display(self.out)
        

    
    def create_table_local(self, table, headers=None, title='', properties={}, hide_header=False, title_font_size='1.25em', index=None):

        if headers is not None:
            df = pd.DataFrame(table, columns=headers)
        else:
            df = pd.DataFrame(table)

        if index is not None:
            df.set_index(index, inplace=True, drop=True)
            df.columns.name = df.index.name
            df.index.name = None

        if hide_header:
            style = df.style.set_caption(title).set_properties(**properties).hide(axis='index').hide(axis='columns').set_table_styles([{
                'selector': 'caption',
                'props': f'caption-side: top; font-size:{title_font_size};'
            }], overwrite=False)
        else:
            style = df.style.set_caption(title).set_properties(**properties).set_table_styles([{
                    'selector': 'caption',
                    'props': f'caption-side: top; font-size:{title_font_size};'
                }], overwrite=False)

        slice_string = style
        return slice_string



    
