#!/bin/bash

cd /in || exit
GO_FILE_PATH="./go.sh"

# Wait for everything to finish booting. I could do this more elegantly I suppose
sleep 10

LOCALIP=$(ifconfig eth0 | grep "inet 192.168.53." | xargs | cut -d' ' -f2)
wget -O /dev/null "http://192.168.53.2:17735/qemuReady?osid=gentoo&ip=""$LOCALIP"

while true
do
	if [ -f "$GO_FILE_PATH" ]; then
		sudo chmod 755 "$GO_FILE_PATH"
		./"$GO_FILE_PATH" &
		wait
		sleep 0.5
		rm -f "$GO_FILE_PATH"
	else
		sleep 0.1
	fi
done
