#!/bin/sh
node=$1
interface=$2
mode=$3
rm -f nohup.out
nohup tcpdump -j adapter_unsynced -U -n --time-stamp-precision nano -i ${interface} "icmp[0] == 8" -w ${node}_${mode}.pcap &
#nohup tcpdump -j adapter_unsynced -U -n --time-stamp-precision nano -i ${interface} -w ${node}.pcap &

# Write tcpdump's PID to a file
echo $! > /var/run/tcpdump.pid
