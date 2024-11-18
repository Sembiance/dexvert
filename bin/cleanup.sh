#!/bin/bash

whoami=$(whoami | tr -d '[:space:]')

kill "$(cat /mnt/dexvert/daemonize_dexserver.pid)"
kill "$(pidof -x dexserver)"
sudo killall -q -9 winedevice.exe services.exe explorer.exe plugplay.exe svchost.exe rpcss.exe sf dosbox
killall Xvfb
killall -9 at-spi-bus-launcher helpdeco gimp-org-file-pnm identify convert 86Box timidity gimp x11vnc uadecore
killall wineserver python3 sf java uniconvertor oosplash soffice.bin texi2dvi DirectorCastRipper.exe pdfetex

if [[ "$(hostname)" == dexdrone* ]]; then
	killall inotifywait dbus-launch dexrecurse deno
fi

cd /mnt/ram/tmp || exit

sudo killall mount
sudo killall -9 mount
sudo umount ./*uniso
sudo umount ./*photocd-info
sudo umount ./*iso/*fuseiso
sudo umount ./*/*
sudo umount ./*
sudo umount -f ./*/*
sudo umount -f ./*
sudo killall mount
sudo killall -9 mount
sudo umount ./*/*
sudo umount ./*
sudo umount -f ./*/*
sudo umount -f ./*
if [[ "$(hostname)" == dexdrone* ]]; then
	rm -rf /mnt/ram/tmp/*
fi
sudo umount ./*/*
sudo umount ./*
if [[ "$(hostname)" == dexdrone* ]]; then
	rm -rf /mnt/ram/tmp/*
fi

cd /tmp || exit
if [[ "$(hostname)" == dexdrone* ]]; then
	rm -f .X*lock
fi
rm -f OSL_PIPE*
fd magick -x rm {} \;
rm -rf Ay_Emul* ./*.tmp xf* scribus* pictto* tmp* temp* clr-debug* dotnet* qtsingle* peazip* calibre* server*.xkm ./*openraster __autograph* __pycache__ ./*.ps uud* gs_* apache-tika-server-forked-tmp*
rm -f ./*.crash.txt
rm -rf .vbox-sembiance-ipc system-commandline-sentinel-files gimp blender* .wine-7777

umount --quiet .mount_ink* 2> /dev/null
rm -rf .mount_ink*

if [[ "$(hostname)" == dexdrone* ]]; then
	cd .X11-unix || exit
	rm -f ./*
fi

cd /mnt/ram || exit
/mnt/compendium/bin/fixPerms
rm -rf dexvert

if [[ "$(hostname)" == dexdrone* ]]; then
	fd . /home/"$whoami"/.dbus/session-bus/ --type=file -x rm {} \;
fi
