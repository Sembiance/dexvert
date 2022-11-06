#!/bin/bash
BASE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$BASE" || exit

# CD ISO: 
# -vnc :14
# File sharing: ,hostfwd=tcp:127.0.0.1:9548-192.168.53.20:548
qemu-system-ppc -machine type=mac99,dump-guest-core=off -m size=1024M -prom-env 'auto-boot?=true' -prom-env 'boot-args=-v' -prom-env 'vga-ndrv?=true' -drive file=hd.img,format=raw,media=disk -netdev user,net=192.168.53.0/24,dhcpstart=192.168.53.20,id=nd1 -device sungem,netdev=nd1 -device usb-mouse -drive file=data/MACPEOPLE-1998-NO2.ISO,format=raw,media=cdrom
