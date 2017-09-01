## For streaming the Pi-Camera from Zero to the 3
### On the 3

run

    nc -l -p 5001 | DISPLAY=:0 mpv -fps 31 -cache 1024 --autofit=786 -
    
change the autofit parameter to the size you like

### On the Zero
Log in from the 3 with -X as parameter for ssh

    ssh -X pi@10.1.0.201
    raspivid -t 0 -o - | nc 10.1.0.1 5001

You can change the IP to any device in the net. 

Make sure that the receiver is up on the 3 before you start the stream on the Zero!
