#!/bin/bash

cd /mnt/compendium/sync || exit
./upload --yes dexdrone1 dexdrone2

function restartDexdrone()
{
	echo "Restarting dexserver on $1..."
	ssh sembiance@dexdrone1 /mnt/compendium/DevLab/dexvert/bin/stopDexserver
	ssh sembiance@dexdrone1 /mnt/compendium/DevLab/dexvert/bin/startDexserver
}

if [ "$2" = "--restart" ]; then
	restartDexdrone dexdrone1 &
	restartDexdrone dexdrone2 &
	wait
fi

echo -e "\nPublishing to dexdrones complete."
