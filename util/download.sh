#!/bin/bash

if [[ -f "$1"".filter" ]]
then
	if [ "$2" = "--yes" ]
	then
		rsync -f "merge ""$1"".filter" --delete -aHv "$1":/mnt/compendium/DevLab/dexvert/ /mnt/compendium/DevLab/dexvert/
	else
		echo "DRY RUN"
		rsync -f "merge ""$1"".filter" --delete -rlpgoDHv --dry-run "$1":/mnt/compendium/DevLab/dexvert/ /mnt/compendium/DevLab/dexvert/
		echo -e "\n\033[1;33mIf the above list looks good, re-run as: \033[1;37m./download.sh ""$1"" --yes"
	fi
else
	echo "Must give a valid remote computer name that has a <name>.filter file"
fi
