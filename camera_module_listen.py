# coding: utf-8

import socket
import struct
import os.path
import sys
import time
import subprocess
import shutil
from operator import truediv

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

DESTINATION_PATH = '/home/pi/scans/'
TEMP_PATH = '/home/pi/'

if __name__ == '__main__':
    print("Starting luaga camera module listener.")
    print("Opening multicast listening socket.")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))  # use MCAST_GRP instead of '' to listen only to MCAST_GRP, not all groups on MCAST_PORT
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        command = sock.recv(1024)
        print("Received multicast command: %s" % command.encode('utf-8'))
        if command == b'capture':
            print("Capturing image")

            error_filename = os.path.join(DESTINATION_PATH, "%s.error" % socket.gethostname())
            temp_filename = os.path.join(TEMP_PATH, "%s.jpg" % socket.gethostname())
            
#            camera_options = ['raspistill',
#                                '-w', '3280',
#                                '-h', '2464',
#                                '-t', '1',
#                                '-n',
#                                '-mm', 'average',
#                                '-awb', 'off',
#                                '-awbg', '1.5,1.5',
#                                '-q', '100',
#                                '-drc', 'off',
#                                '-co', '15',
#                                '-o', temp_filename]
            
            camera_options = ['raspistill', '-o', temp_filename]
            
            if subprocess.call(camera_options) == 0:
                
                print("Saved image to", temp_filename)
                
                delay = int(socket.gethostname()[-2:])
                print("Waiting %s seconds before trying to transfer file" % delay)
                time.sleep(delay)
                
                while True:
                    try:
                        shutil.copy(temp_filename, DESTINATION_PATH)
                        print("Copied Image to", DESTINATION_PATH)
                        break
                    except:
                        print("Unexpected error:", sys.exc_info()[0])
                        print("Copying failed, waiting 0.5s and trying again…")
                        time.sleep(0.5)
            else:
                while True:
                    try:
                        subprocess.call(['touch', error_filename])
                        print("Photograpy failed")
                        break
                    except :
                        print("Unexpected error:", sys.exc_info()[0])
                        print("touching failed, trying again…")
                        time.sleep(0.5)
