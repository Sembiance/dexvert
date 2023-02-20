#!/bin/bash

whoami=$(whoami | tr -d '[:space:]')

killall Xvfb qemu-system-i386 qemu-system-ppc qemu-system-x86_64
killall -9 at-spi-bus-launcher helpdeco gimp-org-file-pnm identify

cd /mnt/ram/tmp || exit
sudo umount ./*uniso
sudo umount ./*iso/*fuseiso
rm -rf ./*

cd /tmp || exit
rm -f .X*lock
fd magick -x rm {} \;
rm -rf cxf* scribus* pictto* tmp* temp* clr-debug* dotnet* qtsingle* peazip* server*.xkm ./*openraster __autograph* __pycache__ ./*.ps uud* gs_* apache-tika-server-forked-tmp*

umount --quiet .mount_ink* 2> /dev/null
rm -rf .mount_ink*

cd .X11-unix || exit
rm -f ./*

cd /mnt/ram || exit
/mnt/compendium/DevLab/dexvert/bin/fixPerms
rm -rf dexvert

fd . /home/"$whoami"/.dbus/session-bus/ --type=file -x rm {} \;
