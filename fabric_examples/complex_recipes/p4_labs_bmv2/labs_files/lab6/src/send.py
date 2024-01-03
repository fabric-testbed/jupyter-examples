#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import netifaces as ni
from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def main():

    if len(sys.argv)<3:
        print('pass 2 arguments: <iface> <src> <destination> "<message>"')
        exit(1)

    iface = str(sys.argv[1]) 
    src_addr = socket.gethostbyname(sys.argv[2])
    dst_addr = socket.gethostbyname(sys.argv[3])
    host_mac_addr =  ni.ifaddresses(iface)[ni.AF_LINK][0]['addr']

    print(("sending on interface %s to %s" % (iface, str(dst_addr))))
    pkt =  Ether(src=host_mac_addr, dst='00:00:00:00:00:02')
    pkt = pkt /IP(src=src_addr,dst=dst_addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / sys.argv[2]
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
