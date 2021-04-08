#!/bin/bash
BASE="/mnt/compendium/DevLab/dexvert/qemu/win2k"

cd "$BASE" || exit
sudo mount -t cifs -o user=dexvert,pass=dexvert,port=9445,vers=1.0,sec=ntlm,gid=1000,uid=7777 //127.0.0.1/in "$BASE"/in
sudo mount -t cifs -o user=dexvert,pass=dexvert,port=9445,vers=1.0,sec=ntlm,gid=1000,uid=7777 //127.0.0.1/out "$BASE"/out

