#!/bin/bash
# A basic bash Programm for the scanner
## ----------------------------------
# Step #1: Define variables
# ----------------------------------
EDITOR=vim
PASSWD=/etc/passwd
RED='\033[0;41;30m'
STD='\033[0;0;39m'
GRN='\033[1;49;32m' 
# ----------------------------------
# Step #2: User defined function
# ----------------------------------
pause(){
        echo -e "${GRN}Press [Enter] key to continue...${STD}"
        read -p ""
}

# check if scanners are started and luaga_listen is running on them
luaga_listen(){
        ansible scanners -m systemd -a "name=luaga-listen state=started" -u pi --become -f 10 > ansible_log
        cat ansible_log | sed ':again;$!N;$!b again; :b; s/{[^{}]*}//g; t b' | sed s/'10.1.0.2'/''/ | sed s/'\s=>'/''/ | sort
        pause
}
 
# send command to make picture
cheese(){
        python send_multicast_capture_command.py
        watch -d -t -n 1 'ls -la /home/pi/scans'
        move_files
        pause
}

#push pics where they should go
move_files(){
        current_time=$(date "+%Y-%m-%d_%H-%M")
        mkdir /home/pi/scans/finished/scan_$current_time
        mv /home/pi/scans/*.jpg /home/pi/scans/finished/scan_"$current_time"
        clear
        amount=$(ls /home/pi/scans/finished/scan_"$current_time" | wc -l)
        echo "Copied $amount pictures"
}

# Shutdown procedure
shutdown(){
        ansible scanners -a "shutdown" -u pi --become -f 10 > shutdown_log
        cat shutdown_log | sed ':again;$!N;$!b again; :b; s/{[^{}]*}//g; t b' | sed s/'10.1.0.2'/''/ | sed s/'\s=>'/''/ | sort
        echo -e "${RED}Press [Enter] to shutdown RaspiThree!${STD}"
        read -p ""
        sudo shutdown -Ph now
} 

# function to display menus
show_menus() {
        clear
        echo "~~~~~~~~~~~~~~~~~~~~~"
        echo " M A I N - M E N U"
        echo "~~~~~~~~~~~~~~~~~~~~~"
        echo "1. Test Scanners"
        echo "2. Make a picture"
        echo "3. Shutdown"
        echo "4. Exit program"
        }
# read input from the keyboard and take a action
# invoke luaga_listen when the user select 1 from the menu option.
# invoke cheese when the user select 2 from the menu option.
# invoke shutdown when the user select 3 from the menu option.
# Exit when user the user select 4 form the menu option.
read_options(){
        local choice
        read -p "Enter choice [ 1 - 4] " choice
        case $choice in
                1) luaga_listen ;;
                2) cheese ;;
                3) shutdown ;;
                4) exit 0;;
                *) echo -e "${RED}Error...${STD}" && sleep 2
        esac
}
 
# ----------------------------------------------
# Step #3: Trap CTRL+C, CTRL+Z and quit singles
# ----------------------------------------------
trap '' SIGINT SIGQUIT SIGTSTP
 
# -----------------------------------
# Step #4: Main logic - infinite loop
# ------------------------------------
while true
do
 
        show_menus
        read_options
done
