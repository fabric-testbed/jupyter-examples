#!/bin/python3

import os
import sys

import json
import time
import paramiko

import pandas as pd

from datetime import datetime
from dateutil import tz

def create_table_local(table, headers=None, title='', properties={}, hide_header=False, title_font_size='1.25em', index=None):
        
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

def iperf3_process_output(output_dir='output', verbose=False):
    
    files = os.listdir(output_dir)   
                  
    run_suffix = '_client_summary_output' 
    runs = {}                
    for file in files:
        if file.endswith(run_suffix):
            run_name = file.removesuffix(run_suffix)
            
            #open text file in read mode
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
        
        table.append( [    run_name,
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
    headers=["Name",  "P", "pmtu",  "bw", "rtt_max", "rtt_min", "rtt_mean", "retransmits" ]
    printable_table = create_table_local(table, title=f'iperf3 tests', properties={'text-align': 'left'}, headers=headers, index='Name')
    display(printable_table)

            
    
    
        
            
        


    
def iperf3_run(source_node=None, target_node=None, target_ip=None, w=None, P=1, t=60, i=10, O=None, verbose=False):
    
    run_name=f"{source_node.get_name()}_{target_node.get_name()}_{datetime.now(tz=tz.tzutc()).strftime('%Y%m%d%H%M')}"

    target_thread = target_node.execute_thread(f'./fabric_node_tools/iperf3_server.sh {run_name} {P}')
    
    # Make sure the target is running before the source starts
    time.sleep(10)
    
    net_name = f"{target_node.get_site()}_net"

    retry = 3
    while retry > 0:
        command = f'./fabric_node_tools/iperf3_client.sh {run_name} {target_ip} {P} -t {t} -i {i}'
        #command = f'iperf -J -t {t} -i {i} -c {target_ip} -P {P}'
        if O != None:
            command = f'{command} -O {O}'
           
        if w != None:
            command = f'{command} -w {w}'
        
        print(f"{command}")
        
        source_thread = source_node.execute_thread(command)

        source_stdout, source_stderr = source_thread.result()

        #print(f"source_stdout: {source_stdout}")
        #print(f"source_stderr: {source_stderr}")


        #if 'error' in json.loads(source_stdout).keys():
        #    print(f"{source_node.get_name()} -> {target_node.get_name()} {target_ip}: error: {json.loads(source_stdout)['error']}")
        #    retry = retry - 1
        #    time.sleep(5)
        #    continue

        break
        
        

    print(f"source_stderr: {source_stderr}")

    # Start target thread
    target_stdout, target_stderr = target_thread.result()
    print(f"target_stderr: {target_stderr}")
    
    time.sleep(10)

    
    source_node.download_file(f'./output/{run_name}_client_summary_output',f'{run_name}_client_summary_output')
    target_node.download_file(f'./output/{run_name}_server_summary_output',f'{run_name}_server_summary_output')

    
    
    
    
    #print(f"{source_stdout}")
    #print(f"{target_stdout}")
    
   
        

    
    #return iperf3_output


