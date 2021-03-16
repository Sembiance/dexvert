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

echo "Servers running..."

trap 'kill "$pid1" "$pid2" "$pid3"; echo done; exit 1' SIGINT
wait
