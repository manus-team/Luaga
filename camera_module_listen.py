# coding: utf-8

import socket
import struct
import picamera
import os.path
from operator import truediv

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

DESTINATION_PATH = '/home/pi/scans/'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))  # use MCAST_GRP instead of '' to listen only to MCAST_GRP, not all groups on MCAST_PORT
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

while True:
	command = sock.recv(1024)
	if command == b'capture':
		print("Capturing image")
		camera = picamera.PiCamera()
		camera.resolution = (3280,2464)   # The full 8MP resolution causes problems unless the pi’s GPU is allocated more memory…
		#camera.resolution = (2592,1944)  # …in which case the lower 5MP resolution is required.
		camera.sensor_mode = 2
		camera.framerate = 15
		camera.exposure_mode = 'off'
		camera.awb_mode = 'off'
		
		camera.iso = int(200)
		camera.shutter_speed = int(14000)
		camera.awb_mode = 'off'
		camera.awb_gains = (truediv(int(18),10),truediv(int(14),10))
		camera.drc_strength = 'off'
		
		camera.capture(os.path.join(DESTINATION_PATH, "1.jpg"), format='jpeg', quality=int(100))
		print("Saved image to ", os.path.join(DESTINATION_PATH, "1.jpg"))
		camera.close()
