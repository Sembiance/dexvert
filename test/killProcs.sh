#!/bin/bash
killall Xvfb
killall dosbox
killall ffmpeg
killall scribus
killall convert
killall abydosconvert

# Kill all wine services
find /mnt/compendium/DevLab/dexvert/wine/ -iname "*.exe" -printf '%f\n' | uniq | parallel killall -q {} \;
killall wineserver
killall services.exe
killall winedevice.exe
killall plugplay.exe
killall winedevice.exe
killall svchost.exe
killall rpcss.exe
killall wineboot.exe

# These particular procs have been known to hang
killall pdfpsai.bin
