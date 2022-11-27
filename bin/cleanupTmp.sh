#!/bin/bash

#cd /mnt/ram/tmp || exit
#rm -rf ./*

cd /tmp || exit
rm -f .X*lock
rm -rf cxf* scribus* pictto* tmp* temp* clr-debug* dotnet* qtsingle* peazip*
umount .mount_ink*
rm -rf .mount_ink*

cd .X11-unix || exit
rm -f ./*

fd . /home/sembiance/.dbus/session-bus/ --type=file -x rm {} \;
