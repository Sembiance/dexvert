#!/bin/bash

./dexserv &
pid1=$!

python ../tensor/tensorServer.py &
pid2=$!

trap 'kill "$pid1" "$pid2"; echo done; exit 1' SIGINT
wait
