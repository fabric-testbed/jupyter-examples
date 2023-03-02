#!/usr/bin/env python3

import json
import subprocess
import argparse
import os

parser = argparse.ArgumentParser(description='Move interfaces to a specified namespace and save their configurations.')
parser.add_argument('-d','--config_dir', type=str, default='ip_config/routes',
                    help='direcory to store json file in')
parser.add_argument('-f','--route_file', type=str, default='routes.json',
                    help='json file to save routes')
args = parser.parse_args()
                    
os.makedirs(args.config_dir, exist_ok=True)


# Save the interface configuration to a JSON file
#ip -j -p route list > routes.config
cmd = ["ip", "-j", "route", "list" ]
process = subprocess.Popen(cmd,
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE)
process.wait()
stdout, stderr = process.communicate()
errcode = process.returncode

config = json.loads(stdout.decode())
json_file = f"{args.config_dir}/{args.route_file}"

with open(json_file, 'w') as f:
    json.dump(config, f)
