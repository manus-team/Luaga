# Luaga 3D Scanner

This project contains the software necessary for both the controlling pi (a Raspberry 3)
and the scanning pis (Raspberry Zeros).

## Undocumented: 
Which Python Version is used?
    Something like Python 3 I guess

Which file is doing what and why?


Where are the files loacted and is there location in the $PATH variable?
on the 3:
ansible_log
dnsmasq.leases
cameratest.py
camStream.sh

Pictures are getting first saved in home on the Zeros first and then get transported (by what or whom) to the /scans folder on the 3.

Where? On the 3 there is a config file for dhcp where all mac addresses and there associated IP-Adresses are listed.

On the 3 there is dnsmasq as a dhcp-server running ??  To check if it's running use systemctl status dnsmasq.service
dnsmasq.conf
zeros.conf 

On the 3 there is a file /etc/network/interfaces where e.g. the broadcast Address defined.

The scanner.sh is a Bashscript on the 3 (written by Noah). It allows to check the connections of the Zeros to the Pi3, to scan and to shutdown the Zeros and the Pi3. Contr+C to stop this Program is disabled. 

To check which Pis are connected you can scan the wlanTele2-network (if you are in as well) with "nmap -sn 192.168.1.0/24 


## Hardware+Software Setup

## Mit Dd unter Linux RasPi-Image sichern...
$ sudo dd if=/dev/sdd of=~/raspberry-pi.img

## Mit Dd unter Linux RasPi-Image wiederherstellen...
$ sudo dd if=~/raspberry-pi.img of=/dev/sdd
$ sync


One Raspberry Pi 3 B with an additional network card, creating a wifi network called luaga. Several Raspberry Pi Zero Ws with camera modules set up on the scanner, each connected to the luaga network, with IP addresses 10.1.0.201-2XX, with DHCP-configured hostnames matching their IP address (i.e. luaga01). The 3 creates an NFS share to which the Zeros connect.

The configuration on the Zeros is managed with Ansible (installed on the 3), and is currently done via ad-hoc commands which at some point should probably be written into playbooks for ease of use. There are three ansible groups configured, scanners, scanner1-10 and scanner11-20. The last two groups are for testing convenience.

The Zeros should in theory run listen.py on startup, which listens on a multicast group and takes a photo into the scans folder, named with their hostname, every time the "capture" command is received. 

Number 1 has an older Version of the image and a GUI-Installed for Camerafocus tests.

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

```bash
ansible scanners -a "shutdown" -u pi --become -f 10 
```


## Known Issues

### No pictures is taken
Sometimes raspistill seems to not be able to take a picture. Reason unknown, debugging necessary.

### Weird image problems

Occasionally, blocks of pixels in some images seem to get mixed up and the images come out weird.

### 
