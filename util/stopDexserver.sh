#!/bin/bash
if [ -f /mnt/ram/dexvert/dexserver.pid ]; then
	kill -SIGTERM "$(cat /mnt/ram/dexvert/dexserver.pid)"
else
	echo "Couldn't locate dexserver.pid"
fi
