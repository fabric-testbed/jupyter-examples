#!/usr/bin/env python3

import json
import subprocess
import argparse

parser = argparse.ArgumentParser(description='Move interfaces to a specified namespace and save their configurations.')
parser.add_argument('--route_file', metavar='route_file', type=str, nargs='routes.json',
                    help='json file to save routes')
args = parser.parse_args()

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
with open(route_file, 'w') as f:
    json.dump(config, f)
