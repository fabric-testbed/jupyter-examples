#!/bin/python3

import os
import sys

import json
import time
import paramiko

import pandas as pd

from datetime import datetime
from dateutil import tz


#from plugins import Plugins
#Plugins.load()


def run_iperf3XXX(source_node=None, target_node=None, target_ip=None, w=None, P=1, t=60, i=10, b=None, verbose=False):
    target_threads = []
    

    target_threads.append(target_node.execute_thread(f'iperf -J -1 -s'))
    
    net_name = f"{target_node.get_site()}_net"

    retry = 3
    while retry > 0:
        
        command = f'iperf -J -t {t} -i {i} -c {target_ip} -P {P}'
        if b != None:
            command = f'{command} -b {b}'
           
        if w != None:
            command = f'{command} -w {w}'
        
        print(f"{command}")
        
        source_thread = source_node.execute_thread(command)

        source_stdout, source_stderr = source_thread.result()

        #print(f"{source_stdout}")

        if 'error' in json.loads(source_stdout).keys():
            print(f"{source_node.get_name()} -> {target_node.get_name()} {target_ip}: error: {json.loads(source_stdout)['error']}")
            retry = retry - 1
            time.sleep(5)
            continue

        break
        
        

    print(f"source_stderr: {source_stderr}")

    # Start target thread
    target_stdout, target_stderr = target_thread.result()
    
    #print(f"{source_stdout}")
    #print(f"{target_stdout}")
    
    iperf3_output = { 'source_output': json.loads(source_stdout),
             'target_output': json.loads(target_stdout)}

    if verbose:
        local_host=iperf3_output['source_output']['start']['connected'][0]['local_host'] 
        remote_host=iperf3_output['source_output']['start']['connected'][0]['remote_host'] 

        pmtu = iperf3_output['source_output']['intervals'][0]['streams'][0]['pmtu'] 
        sender_tcp_congestion = iperf3_output['source_output']['end']['sender_tcp_congestion']
        receiver_tcp_congestion = iperf3_output['source_output']['end']['receiver_tcp_congestion']
        max_rtt = iperf3_output['source_output']['end']['streams'][0]['sender']['max_rtt'] 
        min_rtt = iperf3_output['source_output']['end']['streams'][0]['sender']['min_rtt'] 
        mean_rtt = iperf3_output['source_output']['end']['streams'][0]['sender']['mean_rtt'] 

        sum_bandwidth = iperf3_output['source_output']['end']['sum_sent']['bits_per_second'] 
        retransmits = iperf3_output['source_output']['end']['sum_sent']['retransmits'] 
        
        print("{} ({}) -> {} ({}): pmtu: {}, max_rtt: {:.2f}, min_rtt {:.2f}, mean_rtt {:.2f}, bandwidth {:.2f} Mbps, retrans {}, congestion alg (src/dst) {}/{}".format(source_node.get_name(), 
                                                        local_host, 
                                                        target_node.get_name(), 
                                                        remote_host, 
                                                        pmtu, 
                                                        max_rtt*0.001,
                                                        min_rtt*0.001,
                                                        mean_rtt*0.001,
                                                        sum_bandwidth*0.000001,
                                                        retransmits,
                                                        sender_tcp_congestion, 
                                                        receiver_tcp_congestion))
        
        

    
    return iperf3_output


    

def generate_fabnet_ip_map(slice=None):
    #Note: assumes one network per site named. <site>_net
    ip_map = {}
    for node in slice.get_nodes():
        net_name = f"{node.get_site()}_net"
        #print(f"site: {node.get_site()}")

        ip_addr = get_ip_addr(node=node, dev=node.get_interface(network_name=net_name).get_os_interface())['addr_info'][0]['local']
        print(ip_addr)
        ip_map[node] = ip_addr

    return ip_map

def collect_ping_measurment(source_node=None, target_node=None, network_name=None, count=5):
    target_ip = get_ip_addr(node=target_node, dev=target_node.get_interface(network_name=network_name).get_os_interface())['addr_info'][0]['local']
    
    source_node_results = {}

    print(f"{source_node.get_name()} -> {target_node.get_name()} {target_ip}")
    stdout, stderr = source_node.execute(f'pingparsing {target_ip} -c {count} --icmp-reply  ')
    #print(stdout)
    #print(stderr)

    return json.loads(stdout) 

def collect_ping_measurment_thread(source_node=None, target_node=None, network_name=None, count=5):
    target_ip = get_ip_addr(node=target_node, dev=target_node.get_interface(network_name=network_name).get_os_interface())['addr_info'][0]['local']
    
    source_node_results = {}

    print(f"{source_node.get_name()} -> {target_node.get_name()} {target_ip}")
    return source_node.execute_thread(f'pingparsing {target_ip} -c 5 --icmp-reply  ')
    #print(stdout)
    #print(stderr)

    #return json.loads(stdout) 

def collect_all_ping_measurments(slice=None, count=5):
    #Note: assumes one network per site named. <site>_net
    threads = []
    
    all_results = {}
    ip_map = generate_fabnet_ip_map(slice=slice)
    for source_node in slice.get_nodes():
        source_node_results = {}
        for target_node,target_ip in ip_map.items():
            network_name = f"{target_node.get_site()}_net"
            
            all_results[source_node.get_name()] = {}
            threads[(source_node.get_name(),target_node.get_name())] = collect_ping_measurment_thread(source_node=source_node, 
                                                                                                      target_node=target_node, 
                                                                                                      network_name=network_name,
                                                                                                      count=count)
    
    for (source_node_name,target_node_name),thread in threads.items():
        stdout, stderr  = thread.result()
        #result = json.loads(stdout) 
          
        all_results[source_node_name][target_node_name] = json.loads(stdout) 
        #source_node_results[target_node_name] = json.loads(stdout) 
        
        #source_node_results[target_node.get_name()] = pingparse_results

    #all_results[source_node.get_name()] = source_node_results
        
    return all_results

def print_ping_measurments(all_results):
    for source_node_name, source_node_results in all_results.items():
        for target_node_name, result in source_node_results.items():
            for dst,output in result.items():
                dst_ip = dst
                packet_loss_count = output['packet_loss_count']
                rtt_avg = output['rtt_avg']
                rtt_min = output['rtt_min']
                rtt_max = output['rtt_max']
                rtt_mdev = output['rtt_mdev']

            print(f"{source_node_name} -> {target_node_name}: packet_loss_count = {packet_loss_count}, rtt_ave = {rtt_avg}")
            
    
def install_packages(nodes=[], package_manager='yum', packages=[],  quiet=True):
    
    package_string = ""
    for package in packages:
        package_string = f"{package_string} {package}"
    
    command = 'echo command not set!'
    if package_manager == 'yum':
        command = f'sudo yum -y -q install {package_string}'
    elif package_manager == 'apt-get':
        command = f'sudo apt-get -y -q install {package_string}'
    elif package_manager == 'pip3':
        command = f'sudo pip3 -q  install {package_string}'
    elif package_manager == 'pip':
        command = f'sudo pip -q  install {package_string}'
        
    threads = {}
    for node in nodes:     
        print(f"starting thread {node.get_name()}, command: {command}")
        threads[node]=(node.execute_thread(command))
        
        
    for node,config_thread in threads.items():
        stdout, stderr = config_thread.result()
        print(f"Results from {node.get_name()}")
        print(stdout)
        print(stderr)





def get_paramiko_key(private_key_file=None, private_key_passphrase=None):
    #TODO: This is a bit of a hack and should probably test he keys for their types
    # rather than relying on execptions
    if private_key_passphrase:
        try:
            return paramiko.RSAKey.from_private_key_file(private_key_file,  password=private_key_passphrase)
        except:
            pass

        try:
            return paramiko.ecdsakey.ECDSAKey.from_private_key_file(private_key_file,  password=private_key_passphrase)
        except:
            pass
    else:
        try:
            return paramiko.RSAKey.from_private_key_file(private_key_file)
        except:
            pass

        try:
            return paramiko.ecdsakey.ECDSAKey.from_private_key_file(private_key_file)
        except:
            pass

    raise Exception(f"ssh key invalid: FABRIC requires RSA or ECDSA keys")



def execute(command, retry=3, retry_interval=10, username=None, ip_addr=None, private_key_file=None, private_key_passphrase=None):
    import logging

    for attempt in range(retry):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            
            key = get_paramiko_key(private_key_file=private_key_file, private_key_passphrase=private_key_passphrase)
            client.connect(ip_addr,username=username,pkey = key)

            stdin, stdout, stderr = client.exec_command(command)
            rtn_stdout = str(stdout.read(),'utf-8').replace('\\n','\n')
            rtn_stderr = str(stderr.read(),'utf-8').replace('\\n','\n')

            client.close()

          
            #print(f"rtn_stdout: {rtn_stdout}")
            #print(f"rtn_stderr: {rtn_stderr}")

            return rtn_stdout, rtn_stderr
            #success, skip other tries
            break
        except Exception as e:
            try:
                client.close()
            except:
                logging.debug("Exception in client.close")
                pass
    

            if attempt+1 == retry:
                raise e

            time.sleep(retry_interval)
            pass

    raise Exception("ssh failed: Should not get here")

def upload_file(local_file_path, remote_file_path, retry=3, retry_interval=10, 
                username=None, ip_addr=None, private_key_file=None, private_key_passphrase=None):
    import paramiko
    import time

    #logging.debug(f"upload node: {self.get_name()}, local_file_path: {local_file_path}")

    for attempt in range(retry):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            key = get_paramiko_key(private_key_file=private_key_file, private_key_passphrase=private_key_passphrase)
            client.connect(ip_addr,username=username,pkey = key)

            ftp_client=client.open_sftp()
            file_attributes = ftp_client.put(local_file_path, remote_file_path)
            ftp_client.close()

            client.close()
            return file_attributes
            #success, skip other tries
            break
        except Exception as e:
            try:
                client.close()
            except:
                logging.debug("Exception in client.close")
                pass

            if attempt+1 == retry:
                raise e

            #Fail, try again
            print(f"Fail: {e}")
            #traceback.print_exc()
            time.sleep(retry_interval)
            pass

    raise Exception("scp upload failed")

def download_file(local_file_path, remote_file_path, retry=3, retry_interval=10,
                 username=None, ip_addr=None, private_key_file=None, private_key_passphrase=None):
    import paramiko
    import time

    for attempt in range(retry):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            key = get_paramiko_key(private_key_file=private_key_file, private_key_passphrase=private_key_passphrase)
            client.connect(ip_addr,username=username,pkey = key)

            ftp_client=client.open_sftp()
            file_attributes = ftp_client.get(remote_file_path, local_file_path)
            ftp_client.close()

            client.close()

            return file_attributes
            #success, skip other tries
            break
        except Exception as e:
            try:
                client.close()
            except:
                logging.debug("Exception in client.close")
                pass
        

            if attempt+1 == retry:
                raise e

            #Fail, try again
            print(f"Fail: {e}")
            #traceback.print_exc()
            time.sleep(retry_interval)
            pass

    raise Exception("scp download failed")
    
    
def upload_directory(local_directory_path, remote_directory_path, retry=3, retry_interval=10,
                    username=None, ip_addr=None, private_key_file=None, private_key_passphrase=None):
    import tarfile
    import os

    import tempfile
    #logging.debug(f"upload node: {self.get_name()}, local_directory_path: {local_directory_path}")

    output_filename = local_directory_path.split('/')[-1]
    root_size = len(local_directory_path) - len(output_filename)
    #temp_file = "/tmp/" + output_filename + ".tar.gz"
    
    temp_file = "/tmp/" + next(tempfile._get_candidate_names()) + ".tar.gz"
    
    with tarfile.open(temp_file, "w:gz") as tar_handle:
        for root, dirs, files in os.walk(local_directory_path):
            for file in files:
                tar_handle.add(os.path.join(root, file), arcname = os.path.join(root, file)[root_size:])

    upload_file(temp_file, temp_file, retry, retry_interval, 
                username=username, ip_addr=ip_addr, 
                private_key_file=private_key_file, private_key_passphrase=private_key_passphrase)
    os.remove(temp_file)
    execute("mkdir -p "+remote_directory_path + "; tar -xf " + temp_file + " -C " + remote_directory_path + "; rm " + temp_file, 
            retry, retry_interval, username=username, ip_addr=ip_addr, 
            private_key_file=private_key_file, private_key_passphrase=private_key_passphrase)
    return "success"

def download_directory(local_directory_path, remote_directory_path, retry=3, retry_interval=10,
                      username=None, ip_addr=None, private_key_file=None, private_key_passphrase=None):
    import tarfile
    import os
    #logging.debug(f"upload node: {self.get_name()}, local_directory_path: {local_directory_path}")

    temp_file = "/tmp/unpackingfile.tar.gz"
    execute("tar -czf " + temp_file + " " + remote_directory_path, retry, retry_interval,
            username=username, ip_addr=ip_addr, 
            private_key_file=private_key_file, private_key_passphrase=private_key_passphrase)

    download_file(temp_file, temp_file, retry, retry_interval, username=username, ip_addr=ip_addr, 
                  private_key_file=private_key_file, private_key_passphrase=private_key_passphrase)
    tar_file = tarfile.open(temp_file)
    tar_file.extractall(local_directory_path)

    execute("rm " + temp_file, retry, retry_interval, username=username, ip_addr=ip_addr, 
            private_key_file=private_key_file, private_key_passphrase=private_key_passphrase)
    os.remove(temp_file)
    return "success"




