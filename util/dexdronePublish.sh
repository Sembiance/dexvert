#!/bin/bash

cd /mnt/compendium/sync || exit
./upload --yes dexdrone1 dexdrone2 dexdrone3

function restartDexdrone()
{
	echo "Restarting dexserver on $1..."
	ssh sembiance@"$1" /mnt/compendium/DevLab/dexvert/bin/stopDexserver
}

if [ "$2" = "--restart" ]; then
	restartDexdrone dexdrone1 &
	restartDexdrone dexdrone2 &
	restartDexdrone dexdrone3 &
	wait
fi

echo -e "\nPublishing to dexdrones complete."
