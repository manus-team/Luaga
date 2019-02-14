# Luaga 3D Scanner

This project contains the software necessary for both the controlling pi (a Raspberry 3)
and the scanning pis (Raspberry Zeros).

## Undocumented/to clean up

Which Python Version is used?
* As of 2019-01-31, python 3 and 2.7 are used inconsistently. python3 is used for the `camera_module_listen.py` script started by the luaga-listen service. The `send_multicast_capture_command.py` script fails with python3 but could probably easily be updated to work with it.

What do these files do?
* ansible_log
* dnsmasq.leases
* cameratest.py: must be run on a system with a window system, opens a window with live camera output.
* camStream.sh

The scanner.sh is a Bashscript on the 3 (written by Noah). It allows to check the connections of the Zeros to the Pi3, to scan and to shutdown the Zeros and the Pi3. Contr+C to stop this Program is disabled.

To check which Pis are connected you can scan the wlanTele2-network (if you are in as well) with "nmap -sn 192.168.1.0/24 


## Hardware+Software Setup

### Raspberry Pi 3

One Raspberry Pi 3 B with a USB network card in addition to its internal one, creating a wifi network called `luaga`. These interfaces are defined in `/etc/network/interfaces`, with `wlan1` being the connection to an external WiFi WiFi network, and `wlan0` is the internal `luaga` network, within which the 3’s IP address is `10.1.0.1`.

The 3 is running `dnsmasq` in order to assign static IP addresses to each Pi Zero scanner module. The list of MAC addresses and corresponding IP addresses and hostnames is in `cat /etc/dnsmasq.d/zeros.conf`. If adding more scanners to the system, they will need to get records here. Using dnsmasq in this way allows us to easily use cloned SD card images for all of the scanners, and still give them unique, reliable IDs.

The 3 creates an NFS share to which the Zeros connect, which is mounted at `/home/pi/scans` (the same location as the Zeros).
* I’ve not been able to figure out how this share is created or configured — whoever made this, or who can figure it out: please document here with relevant configuration paths! -- Barnaby

### Raspberry Pi Zero W Scanner Modules

Several Raspberry Pi Zero Ws with camera modules set up on the scanner, each connected to the luaga network, with IP addresses 10.1.0.201-2XX, with DHCP-configured hostnames matching their IP address (i.e. luaga01).

One Raspberry Pi 3 B with an additional network card, creating a wifi network called luaga. Several Raspberry Pi Zero Ws with camera modules set up on the scanner, each connected to the luaga network, with IP addresses 10.1.0.201-2XX, with DHCP-configured hostnames matching their IP address (i.e. luaga01). The 3 creates an NFS share to which the Zeros connect.

The configuration on the Zeros is managed with Ansible (installed on the 3), and is currently done via ad-hoc commands which at some point should probably be written into playbooks for ease of use. There are three ansible groups configured, scanners, scanner1-10 and scanner11-20. The last two groups are for testing convenience.

The scanner modules transfer captured photos (named after their DHCP-assigned hostname) to the 3 by copying them into a NFS-mounted folder shared with the 3. This is configured in `/etc/fstab`.

The Zeros run `camera_module_listen.py` on startup, which listens on a multicast group and takes a photo into the NFS-connected `/home/pi/scans` folder, named with their hostname, every time the "capture" command is received. Copying the photo is delayed by N seconds (where N is the numeric ID of the scanner module, e.g. 1-35) in an attempt to reduce network traffic directly after taking the photo. This seems to work but could be replaced with a more optimal solution in the future, for example the 3 requesting images from the scanner modules one by one.

## Common tasks

### Ensuring the luaga-listen service is running on all scanners

The `luaga-listen` service should start automatically on boot, self-updating software and running the `camera_module_listen.py` script, which stays running and waits for multicast commands. This ansible command ensures that is the case:

    ansible scanners -m systemd -a "name=luaga-listen state=started" -u pi --become -f 10

For more compact output use this command:

    ansible scanners -m systemd -a "name=luaga-listen state=started" -u pi --become -f 10 | grep -B 3 started

### Updating the luaga code on all scanners

The `luaga-listen` service will currently pull the latest version of the code from the 3 every time it is run. In the future this should be replaced with an ansible-based deployment, but for the moment it works. To manually update the code on the scanners from the 3, run this command:

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

### Mit Dd unter Linux RasPi-Image sichern

    $ sudo dd if=/dev/<SD-Karte> of=/home/manu/raspberry-pi.img

### Mit Dd unter Linux RasPi-Image wiederherstellen

    $ sudo dd if=/home/manu/raspberry-pi.img of=/dev/<SD-Karte>
    $ sync


## Known Issues

### Weird image problems

Occasionally, blocks of pixels in some images seem to get mixed up and the images come out weird.

### Network Problems

Especially with the addition of 15 scanners, bringing the total up to 35, it’s become clear that the network is a bottleneck. The exact causes of unreliability have not yet been proven. Here are some starting points for testing and experimenting:

#### Issues when starting many scanner modules at once

The zeros are currently connected to power supplies in two groups, 1-20 and 21-35. We’ve noticed problems both when turning all of them on at once, or when turning all 15 in the second group on at once after the first group are already booted. Turning the first group of 20 on at once seems to work fairly reliably. We saw at least one case of scanners not being assigned IP addresses by the 3.

Watching the CPU monitor on the 3 as scanners are turned on shows alarming spikes up to 91%, so it appears that these problems could be one of three bottlenecks:
* a physical bottleneck caused by noise, interference and signal level
* a hardware bottleneck caused by the WiFi dongle in the Pi 3 not being sufficient for managing such large networks
* a hardware/software CPU bottleneck when dnsmasq has to assign many IP addresses very quickly

#### Issues with multicast commands not being received

We noticed several instances of scanners not receiving the `capture` command over the multicast connection, which obviously prevents them from taking any useful photos. This was sometimes fixed by restarting the device, or by restarting the listener script. A way of debugging multicast connections and membership requests would be handy. 

#### Issues when transferring captured photos via NFS

Assuming the capture command was successfully received by most of the scanners, the network immediately gets filled with up to 35 photos being transferred at once. Even only transferring one photo with no other network traffic seems to take up to 5s. Currently, each scanner delays its transfer by it’s ID number in seconds as a way of clumsily working around this problem, but perhaps either another structure (e.g. the 3 requesting photos one at a time) or a different file transport (e.g. scp) may be faster or more reliable.
