#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: syncToHost <hostname>"
    exit
fi

if [ "$1" == "crystalsummit" ]; then
	if [ "$(ssh crystalsummit mount -t nfs)" != "" ]; then
		echo "Don't run this to crystalsummit while it has compendium mounted!"
		exit
	fi
fi

echo "hd.img are not normally synchronized to "$1" due to the huge size of it."
echo "This script will sync it up to the host, run manually after you finish making updates to it."

echo -e "\nSynching hd.img..."
rsync -av --progress /mnt/compendium/DevLab/dexvert/qemu/gentoo/hd.img sembiance@"$1":/mnt/compendium/DevLab/dexvert/qemu/gentoo/hd.img
