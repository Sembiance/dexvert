#!/bin/bash
killall Xvfb
killall dosbox
killall ffmpeg
killall scribus
killall convert
killall abydosconvert

# Kill all wine services
killall wineserver
killall services.exe
killall winedevice.exe
killall plugplay.exe
killall winedevice.exe
killall svchost.exe
killall rpcss.exe
killall Fony.exe
killall wineboot.exe
killall cpcxfsw.exe

# These particular procs have been known to hang
killall pdfpsai.bin
