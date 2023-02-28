#!/usr/bin/env python3

import json
import subprocess
import argparse

parser = argparse.ArgumentParser(description='Move interfaces to a specified namespace and save their configurations.')
parser.add_argument('--namespace', type=str, default='mynamespace',
                    help='the namespace to move the interfaces to')
parser.add_argument('--config_dir', type=str, default='.',
                    help='the directory to save the JSON configurations to')
parser.add_argument('interfaces', metavar='interface', type=str, nargs='+',
                    help='an interface to be moved')
args = parser.parse_args()

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

    # Move the interface to the specified namespace
    cmd = ["ip",  "link",  "set", "dev", f"{iface}", "netns", f"{args.namespace}"]
    print(cmd)
    process = subprocess.Popen(cmd,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
    process.wait()
    stdout, stderr = process.communicate()
    errcode = process.returncode

    print(f"errcode: {errcode}")
    print(f"stdout: {stdout}")
    print(f"stderr: {stderr}")
