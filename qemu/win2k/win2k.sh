#!/bin/bash
BASE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$BASE" || exit

#  CD ISO: -drive file=WindowsXPSP2.iso,if=ide,media=cdrom
# WIP dir: -drive format=raw,if=ide,file.label=wip,file=fat:rw:"$BASE/wip"
# If need to change floppies, add args: -drive file=Disk01.img,index=0,if=floppy,format=raw -monitor stdio
#   Then on console type: change floppy0 Disk02.img
# -vnc :14
qemu-system-i386 -nodefaults -machine accel=kvm,dump-guest-core=off -rtc base="2021-04-18T10:00:00" -m size=1G -drive format=raw,if=ide,file=hd.img -drive format=raw,if=ide,file=pagefile.img -boot order=c -vga cirrus -netdev user,net=192.168.50.0/24,dhcpstart=192.168.50.20,hostfwd=tcp:127.0.0.1:9445-192.168.50.20:445,id=nd1 -device rtl8139,netdev=nd1
