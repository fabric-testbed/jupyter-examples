#!/usr/bin/env python3

import json
import subprocess
import sys


for interface_file in sys.argv[1:]:
    # Load the JSON configuration file for the interface
    with open(interface_file) as f:
        interface_data = json.load(f)


    # Read the JSON data from a file
    with open(f"{interface_file}", "r") as f:
        ip_output = f.read()

        # Parse the JSON output into a Python dictionary
        ip_info = json.loads(ip_output)[0]

        # Extract the IP address, subnet mask, and MTU from the JSON data
        interface = ip_info["ifname"]
        ip_address = ip_info['addr_info'][0]['local']
        subnet_mask = ip_info['addr_info'][0]['prefixlen']
        
        mtu = ip_info['mtu']
        operstate = ip_info['operstate']


        print(f"{interface}: {ip_address}/{subnet_mask}, {mtu}")


        # Configure the interface with the extracted IP address, subnet mask, and MTU
        cmd = ["ip", "addr", "add", f"{ip_address}/{subnet_mask}", "dev", interface]
        subprocess.run(cmd)
        
        cmd = ["ip", "link", "set", "dev", interface, f"{operstate.lower()}"]
        subprocess.run(cmd)
        
        if mtu:
            cmd = ["ip", "link", "set", "dev", interface, "mtu", f'{mtu}']
            subprocess.run(cmd)
