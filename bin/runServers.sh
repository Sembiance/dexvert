#!/bin/bash

./dexserv &
pid1=$!

python ../tensor/tensorServer.py &
pid2=$!

Xvfb :0 -extension GLX -listen tcp -nocursor -ac -screen 0 1200x800x24 &
pid3=$!

sleep 5

DISPLAY=:0 dbus-launch --exit-with-x11

echo "Servers running..."

trap 'kill "$pid1" "$pid2" "$pid3"; echo done; exit 1' SIGINT
wait
