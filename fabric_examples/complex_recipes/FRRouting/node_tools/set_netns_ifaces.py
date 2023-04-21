#!/usr/bin/env python3

import json
import subprocess
import argparse

parser = argparse.ArgumentParser(description='Move interfaces to a specified namespace and save their configurations.')
parser.add_argument('-n','--netns', type=str, default='fabric',
                    help='the namespace to move the interfaces to')
parser.add_argument('-d','--config_dir', type=str, default='.',
                    help='the directory to save the JSON configurations to')
parser.add_argument('interfaces', metavar='interface', type=str, nargs='+',
                    help='an interface to be moved')
args = parser.parse_args()

for iface in args.interfaces:
    # Move the interface to the specified namespace
    cmd = ["ip",  "link",  "set", "dev", f"{iface}", "netns", f"{args.netns}"]
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
