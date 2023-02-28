#!/usr/bin/env python3

import subprocess
import json
import os
import argparse

# Define the command-line argument for the container name or ID
parser = argparse.ArgumentParser()
parser.add_argument("container", help="the name or ID of the Docker container")
parser.add_argument("new_name", help="the new name for the network namespace")
args = parser.parse_args()

# Get the JSON output of the container's network configuration
#pid = subprocess.check_output(["docker", "inspect", "-f", "{{.State.Pid}}", args.container]).decode().strip()
cmd = ["docker", "inspect", "-f", "{{.State.Pid}}", args.container]
process = subprocess.Popen(cmd,
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE)
process.wait()
stdout, stderr = process.communicate()
errcode = process.returncode

print(f"errcode: {errcode}")
print(f"stdout: {stdout}")
print(f"stderr: {stderr}")

pid = stdout.decode().strip()

# Create the symbolic link to the proc's net directory

link_path = os.path.join("/var/run/netns", args.new_name)
proc_net_path = os.path.join("/proc", str(pid), "ns","net")

try:
    os.makedirs("/var/run/netns") 
except:
    pass

print(pid)
print(f"link_path: {link_path}")
print(f"proc_net_path: {proc_net_path}")

try:
    os.unlink(link_path)
except:
    pass

# os.symlink doesn't work for some reason. Link is made but results in error when moving iface
os.symlink(proc_net_path, link_path)

#cmd = ['ln', '-sf',  str(proc_net_path), str(link_path)]
#cmd = f"sudo ln -sf {proc_net_path} {link_path}"

#for s in cmd: print(f"{s} ", end="")
#print("")
#process = subprocess.Popen(cmd, shell=True, 
#                       stdout=subprocess.PIPE, 
#                       stderr=subprocess.PIPE)
#process.wait()
#stdout, stderr = process.communicate()
#errcode = process.returncode
#
#print(f"errcode: {errcode}")
#print(f"stdout: {stdout}")
#print(f"stderr: {stderr}")
