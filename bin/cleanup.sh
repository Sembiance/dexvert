#!/bin/bash

whoami=$(whoami | tr -d '[:space:]')

kill "$(cat /mnt/dexvert/daemonize_dexserver.pid)"
kill "$(pidof -x dexserver)"
sudo killall -q -9 winedevice.exe services.exe explorer.exe plugplay.exe svchost.exe rpcss.exe sf dosbox
killall Xvfb
killall -9 at-spi-bus-launcher helpdeco gimp-org-file-pnm identify convert 86Box timidity gimp
#killall inotifywait

cd /mnt/ram/tmp || exit
sudo umount ./*uniso
sudo umount ./*photocd-info
sudo umount ./*iso/*fuseiso
rm -rf ./*
sudo umount ./*
sudo umount ./*/*
rm -rf ./*

cd /tmp || exit
rm -f .X*lock
fd magick -x rm {} \;
rm -rf Ay_Emul* ./*.tmp xf* scribus* pictto* tmp* temp* clr-debug* dotnet* qtsingle* peazip* calibre* server*.xkm ./*openraster __autograph* __pycache__ ./*.ps uud* gs_* apache-tika-server-forked-tmp*
rm -f ./*.crash.txt
rm -rf .vbox-sembiance-ipc system-commandline-sentinel-files gimp blender* .wine-7777

umount --quiet .mount_ink* 2> /dev/null
rm -rf .mount_ink*

cd .X11-unix || exit
rm -f ./*

cd /mnt/ram || exit
/mnt/compendium/bin/fixPerms
rm -rf dexvert

fd . /home/"$whoami"/.dbus/session-bus/ --type=file -x rm {} \;
