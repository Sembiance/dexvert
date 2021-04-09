#!/bin/bash
BASE="/mnt/compendium/DevLab/dexvert/qemu/winxp"

cd "$BASE" || exit

#-drive format=raw,if=ide,file.label=wip,file=fat:rw:"$BASE/wip"
qemu-system-i386 -nodefaults -machine accel=kvm,dump-guest-core=off -rtc base=localtime -m size=2G -smp cores=2 -drive format=raw,if=ide,index=0,file=hd.img -boot order=c -vga cirrus -netdev user,net=192.168.51.0/24,dhcpstart=192.168.51.20,hostfwd=tcp:127.0.0.1:9445-192.168.51.20:445,id=nd1 -device rtl8139,netdev=nd1