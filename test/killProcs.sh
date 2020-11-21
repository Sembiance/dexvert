#!/bin/bash
killall Xvfb
killall dosbox
killall ffmpeg
killall scribus

# Kill all wine services
killall wineserver
killall services.exe
killall winedevice.exe
killall plugplay.exe
killall winedevice.exe
killall svchost.exe
killall rpcss.exe

# These particular procs have been known to hang
killall pdfpsai.bin
killall python3.7
