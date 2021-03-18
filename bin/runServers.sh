#!/bin/bash

mkdir -p /tmp/garbageDetected

if [ "$DISPLAY" != ":0" ]
then
	Xvfb :0 -extension GLX -listen tcp -nocursor -ac -screen 0 1200x800x24 &
	pid1=$!
	sleep 5
	DISPLAY=:0 dbus-launch --exit-with-x11
else
	pid1="0"
fi

./dexserv &
pid2=$!

mkdir -p /mnt/ram/tmp/__pycache__
python -X pycache_prefix=/mnt/ram/tmp/__pycache__ ../tensor/tensorServer.py &
pid3=$!

for (( ; ; ))
do
	statusResult=$(curl --silent "http://localhost:17735/status" | jq ".status")
	if [ "$statusResult" = '"a-ok"' ]
	then
		break;
	fi

	sleep 1
done

echo -e "\033[1;32mSERVERS ARE RUNNING!\033[0m"

function clean_up
{
	echo "Signal caught. Killing children..."
	kill "$pid3"
	kill "$pid2"
	if [ "$pid1" != "0" ]; then
		kill "$pid1"
	fi

	echo "Waiting for children to finish..."
	wait

	echo -e "\033[0;32mdone.\033[0m"
	exit 1
}

trap clean_up SIGINT

wait
