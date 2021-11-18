#!/usr/bin/python3
import os
from fabrictestbed.slice_manager import SliceManager, Status, SliceState
import json

bastion_public_addr = 'bastion-1.fabric-testbed.net'
bastion_private_ipv4_addr = '192.168.11.226'
bastion_private_ipv6_addr = '2600:2701:5000:a902::c'
print("Bastion Public Addr:           {}".format(bastion_public_addr))
print("Bastion Private IPv4 Addr:     {}".format(bastion_private_ipv4_addr))
print("Bastion Private IPv6 Addr:     {}".format(bastion_private_ipv6_addr))


bastion_username = 'pruth'
print("Bastion Username:              {}".format(bastion_username))

bastion_key_filename = os.environ['HOME'] + "/.ssh/id_rsa_fabric"
print("Bastion Private Keyfile:       {}".format(bastion_key_filename))

ssh_key_file_priv=os.environ['HOME']+"/.ssh/id_rsa"
print("Experiment Private Keyfile:    {}".format(ssh_key_file_priv))

ssh_key_file_pub=os.environ['HOME']+"/.ssh/id_rsa.pub"
print("Experiment Public Keyfile:     {}".format(ssh_key_file_pub))


ssh_key_pub = None
with open (ssh_key_file_pub, "r") as myfile:
    ssh_key_pub=myfile.read()
    ssh_key_pub=ssh_key_pub.strip()
    
credmgr_host = os.environ['FABRIC_CREDMGR_HOST']
print(f"FABRIC Credential Manager:     {credmgr_host}")

orchestrator_host = os.environ['FABRIC_ORCHESTRATOR_HOST']
print(f"FABRIC Orchestrator:           {orchestrator_host}")
