#!/bin/bash

startAt=$(date +"%s")

mkdir -p /tmp/garbageDetected

KIDPIDS=()

if [ "$DISPLAY" = "" ]
then
	X &
	KIDPIDS+=($!)
	sleep 5
	DISPLAY=:0 dbus-launch --exit-with-x11
fi

../server/server.js &
KIDPIDS+=($!)

mkdir -p /mnt/ram/dexvert/__pycache__
python -X pycache_prefix=/mnt/ram/dexvert/__pycache__ ../tensor/tensorServer.py &

KIDPIDS+=($!)

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

for (( ; ; ))
do
	dexservStatusResult=$(curl --silent "http://localhost:17735/status" | jq ".status")
	tensorStatusResult=$(curl --silent "http://localhost:17736/status" | jq ".status")
	if [ "$dexservStatusResult" = '"a-ok"' ] && [ "$tensorStatusResult" = '"a-ok"' ]
	then
		break;
	fi

	sleep 0.2
done

endAt=$(date +"%s")
startupTimeDuration=$((endAt - startAt))

echo -e "\033[1;32mSERVERS ARE RUNNING!\033[0m (took $startupTimeDuration seconds)"

wait
