#!/bin/bash
BASE="/mnt/compendium/DevLab/dexvert/qemu/win2k"

cd "$BASE" || exit
sudo umount "$BASE"/in
sudo umount "$BASE"/out
