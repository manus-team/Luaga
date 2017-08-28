# Luaga 3D Scanner

This project contains the software necessary for both the controlling pi
and the scanning pis.

## Undocumented:
Which Python Version is used?

Which file is doing what and why?

Where are the files loacted and is there location in the $PATH variable?

## Hardware+Software Setup

One Raspberry Pi 3 B with an additional network card, creating a wifi network called luaga. 20 Raspberry Pi Zero Ws with camera modules set up on the scanner, each connected to the luaga network, with IP addresses 10.1.0.201-220, with DHCP-configured hostnames matching their IP address (i.e. luaga01). The 3 creates an NFS share to which the Zeros connect.

The configuration on the Zeros is managed with Ansible (installed on the 3), and is currently done via ad-hoc commands which at some point should probably be written into playbooks for ease of use. There are three ansible groups configured, scanners, scanner1-10 and scanner11-20. The last two groups are for testing convenience.

The Zeros should in theory run listen.py on startup, which listens on a multicast group and takes a photo into the scans folder, named with their hostname, every time the "capture" command is received.

## Common tasks

### Ensuring the luaga-listen service is running on all scanners

In practise the luaga-listen service doesn’t seem to start correctly on boot and has to be started manually via ansible on every boot, with this command:

    ansible scanners -m systemd -a "name=luaga-listen state=started" -u pi --become -f 10

For a simple output use this command:

    ansible scanners -m systemd -a "name=luaga-listen state=started" -u pi --become -f 10 | grep -B 3 started

### Updating the luaga code on all scanners

The luaga-listen script will currently pull the latest version of the code from the 3 every time it is run. In the future this should be replaced with an ansible-based deployment, but for the moment it works. To manually update the code on the scanners from the 3, run this command:

    ansible scanners -a "git -C /home/pi/luaga pull origin master" -f 10

### Capturing an image

If the luaga-listen service is running on all scanners, then an image can be captured from the three with this command, in the luaga folder:

    python send_multicast_capture_command.py

After a few seconds, the image files will start to arrive in the scans folder on the three. Initially, placeholder files ending with a ~ will be created, then over about 20 seconds, they will be replaced by the final versions of the files.

### Debugging luaga-listen

To get the systemd status report for luaga-listen on all of the scanners, run this command:

    ansible scanners -a "systemctl status luaga-listen" -u pi --become -f 10

### Shutting down the Scanner

To shutdown the Scanner run this command on the 3 and then shutdown itself:

ansible scanners -a "shutdown" -u pi --become -f 10 


## Known Issues

### Some Zeros are not connected

As of 2017-08-27, Zeros number 1 and 20 are not connected to the setup, so no images will be created, and ansible will return errors for them. Number 1 has an older Version of the image and a GUI-Installed for Camerafocus tests. 

### Unknown NFS issue preventing disk IO for some zeros

Often, one or two zeros per scan will be unreliably unable to create files or perform any other IO in the scans folder, either preventing them from being able to create an image file there at all, or only leaving the luagaXX.jpg~ placeholder file, and not the complete one.

* We tested removing 10 pis from the system and capturing, and the issue still occurred, so it doesn’t look like it’s a network issue.

### luaga-listen service not starting automatically on boot

It is definitely enabled, but it seems like when it runs on boot, it doesn’t get run in the correct directory, or from the correct user, for some reason. Starting it any time after boot results in it starting fine.

### Weird image problems

Occasionally, blocks of pixels in some images seem to get mixed up and the images come out weird.
