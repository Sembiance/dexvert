#!/bin/bash
killall Xvfb
killall dosbox
killall ffmpeg
killall scribus
killall convert
killall abydosconvert
killall -9 identify

# These particular procs have been known to hang
killall pdfpsai.bin
