  GNU nano 2.2.6                                            File: luaga/camera_module_listen.py                                                                                      Modified  

# coding: utf-8

import socket
import struct
import os.path
import time
import subprocess
import shutil
from operator import truediv

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

DESTINATION_PATH = '/home/pi/scans/'
TEMP_PATH = '/home/pi/'

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))  # use MCAST_GRP instead of '' to listen only to MCAST_GRP, not all groups on MCAST_PORT
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        command = sock.recv(1024)
        if command == b'capture':
            print("Capturing image")

            error_filename = os.path.join(DESTINATION_PATH, "%s.error" % socket.gethostname())
            temp_filename = os.path.join(TEMP_PATH, "%s.jpg" % socket.gethostname())

            if subprocess.call(['raspistill', '-w', '3280', '-h', '2464', '-t', '1', '-n', '-sh', '30', '-co', '30', '-ISO', '100', '-q', '100', '-o', temp_filename]) == 0:
                print("Saved image to", temp_filename)
                while True:
                    try:
                        shutil.copy(temp_filename, DESTINATION_PATH)
                        print("Copied Image to", DESTINATION_PATH)
                        break
                    except OSError:
                        print("Copying failed, trying again ...")
            else:
                subprocess.call(['touch', error_filename])
                print("Photograpy failed")
