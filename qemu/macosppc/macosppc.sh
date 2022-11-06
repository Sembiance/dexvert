#!/bin/bash
BASE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$BASE" || exit

# CD ISO: -drive file=data/macos-922-uni.iso,format=raw,media=cdrom
# -vnc :14
# File sharing: ,hostfwd=tcp:127.0.0.1:9548-192.168.53.20:548
qemu-system-ppc -machine type=mac99,dump-guest-core=off -m size=1024M -prom-env 'auto-boot?=true' -prom-env 'boot-args=-v' -prom-env 'vga-ndrv?=true' -drive file=hd.img,format=raw,media=disk -netdev user,net=192.168.53.0/24,dhcpstart=192.168.53.20,id=nd1,hostfwd=tcp:127.0.0.1:9548-192.168.53.20:548 -device sungem,netdev=nd1 -device usb-mouse
