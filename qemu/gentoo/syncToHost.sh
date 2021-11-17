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

echo "hd.img and extract.img are not normally synchronized to "$1", this will do that."
echo "Should probably run this after any changes to the HD."

echo -e "\nSynching hd.img..."
rsync --progress /mnt/compendium/DevLab/dexvert/qemu/gentoo/hd.img sembiance@"$1":/mnt/compendium/DevLab/dexvert/qemu/gentoo/hd.img

echo -e "\nSynching extra.img..."
rsync --progress /mnt/compendium/DevLab/dexvert/qemu/gentoo/extra.img sembiance@"$1":/mnt/compendium/DevLab/dexvert/qemu/gentoo/extra.img
