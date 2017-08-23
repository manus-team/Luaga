# coding: utf-8

import socket
import struct

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

if __name__ == "__main__":
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
	# Force the socket to use the internal interface, i.e. the wifi network created by the pi3.
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton('10.1.0.1'))
	
	# Send the capture command to the multicast group.
	sock.sendto("capture", (MCAST_GRP, MCAST_PORT))
