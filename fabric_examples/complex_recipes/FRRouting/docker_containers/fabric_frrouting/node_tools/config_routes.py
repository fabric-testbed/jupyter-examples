#!/usr/bin/env python3

import json
import subprocess
import sys

def configure_routes(json_file):
    # Open the JSON file and parse the data
    with open(json_file) as f:
        data = json.load(f)

    # Iterate over the list of routes and configure each one
    for route in data:
        try:
            command = ['ip', 'route', 'add']
            command += route['dst'].split('/')
            command += ['via', route['gateway']]
            subprocess.run(command)
        except Exception as e:
            print(f"Failed to add: \n{json.dumps(route,indent=4)}")

if __name__ == '__main__':
    # Check for the required command-line argument
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <json_file>")
        sys.exit(1)

    # Call the configure_routes function with the specified JSON file
    configure_routes(sys.argv[1])
