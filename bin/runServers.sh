#!/bin/bash

mkdir -p /tmp/garbageDetected

KIDPIDS=()

if [ "$DISPLAY" != ":0" ]
then
	Xvfb :0 -extension GLX -listen tcp -nocursor -ac -screen 0 1200x800x24 &
	KIDPIDS+=($!)
	sleep 5
	DISPLAY=:0 dbus-launch --exit-with-x11
fi

../server/server.js &
KIDPIDS+=($!)

mkdir -p /mnt/ram/dexvert/__pycache__
python -X pycache_prefix=/mnt/ram/dexvert/__pycache__ ../tensor/tensorServer.py &

KIDPIDS+=($!)

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
	for kidpid in "${KIDPIDS[@]}"; do
		kill "$kidpid"
	done

	echo "Waiting for children to finish..."
	wait

	echo -e "\033[0;32mdone.\033[0m"
	exit 1
}

trap clean_up SIGINT

wait
