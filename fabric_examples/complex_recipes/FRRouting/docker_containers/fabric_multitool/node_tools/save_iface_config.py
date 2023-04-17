#!/usr/bin/env python3

import json
import subprocess
import argparse
import os

parser = argparse.ArgumentParser(description='Save the configuration of the ifaces.')
parser.add_argument('-d','--config_dir', dest='config_dir', type=str, default='ip_config/ifaces',
                    help='the directory to save the JSON configurations to')
parser.add_argument('interfaces', metavar='interface', type=str, nargs='+',
                    help='an interface to be moved')
args = parser.parse_args()

os.makedirs(args.config_dir, exist_ok=True)

for iface in args.interfaces:
    # Save the interface configuration to a JSON file
    cmd = ["ip", "-j", "addr", "show", f"{iface}" ]
    process = subprocess.Popen(cmd,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
    process.wait()
    stdout, stderr = process.communicate()
    errcode = process.returncode
    
    config = json.loads(stdout.decode())
    json_file = f"{args.config_dir}/{iface}.json"
    with open(json_file, 'w') as f:
        json.dump(config, f)