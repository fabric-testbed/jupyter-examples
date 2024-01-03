#!/bin/bash

set -xe

#ifconfig $1 multicast allmulti promisc mtu 1500 up
ethtool -K $1 rx off		# RX checksumming
ethtool -K $1 tx off		# TX checksumming
ethtool -K $1 sg off		# scatter gather
ethtool -K $1 tso off		# TCP segmentation offload
ethtool -K $1 ufo off		# UDP fragmentation offload
ethtool -K $1 gso off		# generic segmentation offload
ethtool -K $1 gro off		# generic receive offload
ethtool -K $1 lro off		# large receive offload
ethtool -K $1 rxvlan off	# RX Vlan acceleration
ethtool -K $1 txvlan off	# TX vlan acceleration
ethtool -K $1 ntuple off	# RX ntuple filters and actions
ethtool -K $1 rxhash off	# RX hashing offload
ethtool --set-eee $1 eee off	# Energy Efficient Ethernet
