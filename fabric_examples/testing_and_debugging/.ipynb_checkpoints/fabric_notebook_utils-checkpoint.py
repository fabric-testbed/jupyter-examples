#!/usr/bin/python3
import os
from fabrictestbed.slice_manager import SliceManager, Status, SliceState
import json
import sys

import ast

import paramiko
from ipaddress import ip_address, IPv4Address


#module_path = os.path.abspath(os.path.join('.'))
#if module_path not in sys.path:
#    sys.path.append(module_path)

#import fabric_notebook_config as notebook


#!/usr/bin/python3
import os
from fabrictestbed.slice_manager import SliceManager, Status, SliceState
import json

bastion_public_addr = 'bastion-1.fabric-testbed.net'
bastion_private_ipv4_addr = '192.168.11.226'
bastion_private_ipv6_addr = '2600:2701:5000:a902::c'
print("Bastion Public Addr:           {}".format(bastion_public_addr))
print("Bastion Private IPv4 Addr:     {}".format(bastion_private_ipv4_addr))
print("Bastion Private IPv6 Addr:     {}".format(bastion_private_ipv6_addr))


bastion_username = '<XXXX ADD YOUR LOGIN ID XXXX>'
print("Bastion Username:              {}".format(bastion_username))

bastion_key_filename = os.environ['HOME'] + "/.ssh/id_rsa_fabric"
print("Bastion Private Keyfile:       {}".format(bastion_key_filename))

ssh_key_file_priv=os.environ['HOME']+"/.ssh/id_rsa"
print("Experiment Private Keyfile:    {}".format(ssh_key_file_priv))

ssh_key_file_pub=os.environ['HOME']+"/.ssh/id_rsa.pub"
print("Experiment Public Keyfile:     {}".format(ssh_key_file_pub))


ssh_key_pub = None
with open (ssh_key_file_pub, "r") as myfile:
    ssh_key_pub=myfile.read()
    ssh_key_pub=ssh_key_pub.strip()

credmgr_host = os.environ['FABRIC_CREDMGR_HOST']
print(f"FABRIC Credential Manager:     {credmgr_host}")

orchestrator_host = os.environ['FABRIC_ORCHESTRATOR_HOST']
print(f"FABRIC Orchestrator:           {orchestrator_host}")



def validIPAddress(IP: str) -> str:
    try:
        return "IPv4" if type(ip_address(IP)) is IPv4Address else "IPv6"
    except ValueError:
        return "Invalid"

def execute_script(node_username, node, script):
    import paramiko

    try:
        management_ip = str(node.get_property(pname='management_ip'))
        #print("Node {0} IP {1}".format(node.name, management_ip))

        key = paramiko.RSAKey.from_private_key_file(ssh_key_file_priv)

        bastion=paramiko.SSHClient()
        bastion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        bastion.connect(bastion_public_addr, username=bastion_username, key_filename=bastion_key_filename)

        bastion_transport = bastion.get_transport()
        if validIPAddress(management_ip) == 'IPv4':
            src_addr = (bastion_private_ipv4_addr, 22)
        elif validIPAddress(management_ip) == 'IPv6':
            src_addr = (bastion_private_ipv6_addr, 22)
        else:
            return 'Management IP Invalid: {}'.format(management_ip)

        dest_addr = (management_ip, 22)
        bastion_channel = bastion_transport.open_channel("direct-tcpip", dest_addr, src_addr)


        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(management_ip,username=node_username,pkey = key, sock=bastion_channel)

        stdin, stdout, stderr = client.exec_command('echo \"' + script + '\" > script.sh; chmod +x script.sh; sudo ./script.sh')
        stdout_str = str(stdout.read(),'utf-8').replace('\\n','\n')
        #print ('')
        #print (str(stdout.read(),'utf-8').replace('\\n','\n'))
        #print (stdout_str)

        client.close()
    except Exception as e:
        print(str(e))
        return str(e)

    return stdout_str


def upload_file(node_username, node, local_file_path, remote_file_path):
    import paramiko

    try:
        management_ip = str(node.get_property(pname='management_ip'))
        #print("Node {0} IP {1}".format(node.name, management_ip))

        key = paramiko.RSAKey.from_private_key_file(ssh_key_file_priv)

        bastion=paramiko.SSHClient()
        bastion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        bastion.connect(bastion_public_addr, username=bastion_username, key_filename=bastion_key_filename)

        bastion_transport = bastion.get_transport()
        if validIPAddress(management_ip) == 'IPv4':
            src_addr = (bastion_private_ipv4_addr, 22)
        elif validIPAddress(management_ip) == 'IPv6':
            src_addr = (bastion_private_ipv6_addr, 22)
        else:
            return 'Management IP Invalid: {}'.format(management_ip)

        dest_addr = (management_ip, 22)
        bastion_channel = bastion_transport.open_channel("direct-tcpip", dest_addr, src_addr)


        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(management_ip,username=node_username,pkey = key, sock=bastion_channel)

        ftp_client=client.open_sftp()
        file_attributes = ftp_client.put(local_file_path, remote_file_path)
        ftp_client.close()

        client.close()
    except Exception as e:
        print(str(e))
        return str(e)

    return file_attributes

def download_file(node_username, node, local_file_path, remote_file_path):
    import paramiko

    try:
        management_ip = str(node.get_property(pname='management_ip'))
        #print("Node {0} IP {1}".format(node.name, management_ip))

        key = paramiko.RSAKey.from_private_key_file(ssh_key_file_priv)

        bastion=paramiko.SSHClient()
        bastion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        bastion.connect(bastion_public_addr, username=bastion_username, key_filename=bastion_key_filename)

        bastion_transport = bastion.get_transport()
        if validIPAddress(management_ip) == 'IPv4':
            src_addr = (bastion_private_ipv4_addr, 22)
        elif validIPAddress(management_ip) == 'IPv6':
            src_addr = (bastion_private_ipv6_addr, 22)
        else:
            return 'Management IP Invalid: {}'.format(management_ip)

        dest_addr = (management_ip, 22)
        bastion_channel = bastion_transport.open_channel("direct-tcpip", dest_addr, src_addr)


        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(management_ip,username=node_username,pkey = key, sock=bastion_channel)

        ftp_client=client.open_sftp()
        file_attributes = ftp_client.get(local_file_path, remote_file_path)
        ftp_client.close()

        client.close()
    except Exception as e:
        print(str(e))
        return str(e)

    return file_attributes

import time
def wait_for_slice(slice, slice_manager=None ,timeout=180,interval=10,progress=False):
    timeout_start = time.time()

    slice_name = slice.slice_name

    if progress: print("Waiting for slice .", end = '')
    while time.time() < timeout_start + timeout:
        return_status, slices = slice_manager.slices(excludes=[SliceState.Dead,SliceState.Closing])

        if return_status == Status.OK:
            slice = list(filter(lambda x: x.slice_name == slice_name, slices))[0]
            if slice.slice_state == "StableOK":
                if progress: print(" Slice state: {}".format(slice.slice_state))
                return slice
            if slice.slice_state == "Closing" or slice.slice_state == "Dead":
                if progress: print(" Slice state: {}".format(slice.slice_state))
                return slice
        else:
            print(f"Failure: {slices}")

        if progress: print(".", end = '')
        time.sleep(interval)

    if time.time() >= timeout_start + timeout:
        if progress: print(" Timeout exceeded ({} sec). Slice: {} ({})".format(timeout,slice.slice_name,slice.slice_state))
        return slice


def find_nic_mapping(node1=None, node1_username='ubuntu', node1_vlan=None, node2=None, node2_username='ubuntu', node2_vlan=None, ):
    node1_ip = '192.168.42.1'
    node2_ip = '192.168.42.2'
    cidr = '24'

    #print("node1: {}".format(node1))
    #print("node1_username: {}".format(node1_username))

    stdout = execute_script(node1_username, node1, 'sudo python3 fabric_vm_utils.py {}'.format('get_datalane_ifaces') )
    node1_dataplane_ifaces = ast.literal_eval(stdout)

    stdout = execute_script(node2_username, node2, 'sudo python3 fabric_vm_utils.py {}'.format('get_datalane_ifaces') )
    node2_dataplane_ifaces = ast.literal_eval(stdout)

    print("node1_dataplane_ifaces: {}".format(node1_dataplane_ifaces))
    print("node2_dataplane_ifaces: {}".format(node2_dataplane_ifaces))

    for n1_iface in node1_dataplane_ifaces:
        stdout = execute_script(node1_username, node1, 'sudo python3 fabric_vm_utils.py {}'.format('flush_all_ifaces') )

        if node1_vlan:
            node1_iface_full = str(n1_iface) + '.' + str(node1_vlan)
            stdout = execute_script(node1_username, node1, 'sudo python3 fabric_vm_utils.py {} {} {}'.format('create_vlan_iface', n1_iface, node1_vlan) )
            stdout = execute_script(node1_username, node1, 'sudo python3 fabric_vm_utils.py {} {} {} {}'.format('set_iface_addr',node1_ip,cidr,n1_iface+'.'+str(node2_vlan)) )
        else:
            node1_iface_full = str(n1_iface)
            stdout = execute_script(node1_username, node1, 'sudo python3 fabric_vm_utils.py {} {} {} {}'.format('set_iface_addr',node1_ip,cidr,n1_iface) )

        for n2_iface in node2_dataplane_ifaces:
            stdout = execute_script(node2_username, node2, 'sudo python3 fabric_vm_utils.py {}'.format('flush_all_ifaces') )

            if node2_vlan:
                node2_iface_full = str(n2_iface) + '.' + str(node2_vlan)
                stdout = execute_script(node2_username, node2, 'sudo python3 fabric_vm_utils.py {} {} {}'.format('create_vlan_iface', n2_iface, node2_vlan) )
                stdout = execute_script(node2_username, node2, 'sudo python3 fabric_vm_utils.py {} {} {} {}'.format('set_iface_addr',node2_ip,cidr,n2_iface+'.'+str(node2_vlan)) )
            else:
                node2_iface_full = str(n2_iface)
                stdout = execute_script(node2_username, node2, 'sudo python3 fabric_vm_utils.py {} {} {} {}'.format('set_iface_addr',node2_ip,cidr,n2_iface) )


            #ping test
            stdout = execute_script(node2_username, node2, 'sudo python3 fabric_vm_utils.py {} {}'.format('ping_test',node1_ip) )
            try:
                f = float(stdout.replace('\n',''))
                print("Node1: {}, Node2: {}, rtt {}, Success! ".format(node1_iface_full,node2_iface_full,f))
            except ValueError:
                print("Fail! Node1: {}, Node2: {}, Fail! ".format(node1_iface_full,node2_iface_full))
                #print ("Not a float")
                pass




            if node2_vlan:
                stdout = execute_script(node2_username, node2, 'sudo python3 fabric_vm_utils.py {} {} {}'.format('delete_vlan_iface', n2_iface, node2_vlan) )

        if node1_vlan:
            stdout = execute_script(node1_username, node1, 'sudo python3 fabric_vm_utils.py {} {} {}'.format('delete_vlan_iface', n1_iface, node1_vlan) )


def ping_test(node, ping_target_ip, verbose=False):
    if verbose: print("Ping Test: {}".format(ping_target_ip),end='')


    #rtt min/avg/max/mdev = 0.063/0.119/0.189/0.053 ms
    #output = "Information about latency with ping: \n"

    try:
        #ping up
        raw_output = execute_script(username, node, 'ping -c 3 ' + ping_target_ip + ' | grep rtt')
        #raw_output = stdout.read().decode("utf-8")
        raw_data = raw_output.split(" ")[3]
        data_array = raw_data.split("/")
        avg_rtt = data_array[1]

        if verbose: print(", ping success! avg_rtt: {}".format(avg_rtt))
    except Exception as e:
        if verbose: print(", ping failed: {}".format(str(e)))
        return float(0)

    return float(avg_rtt)
