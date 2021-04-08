#!/bin/bash
# shellcheck disable=SC2181

BASE="/mnt/compendium/DevLab/dexvert/qemu/win2k"

cd "$BASE" || exit

#echo "Note, the wip dir only is loaded into QEMU once on boot. Use mountInOut.sh for back and forth file access"
#
#-drive format=raw,if=ide,file.label=wip,file=fat:rw:"$BASE/wip"
#,hostfwd=tcp:127.0.0.1:4445-10.0.2.15:445
#,hostfwd=tcp:127.0.0.1:12021-10.0.2.15:21
qemu-system-i386 -nodefaults -drive format=raw,if=ide,index=0,file=hd.img -boot order=c -vga cirrus -netdev user,net=192.168.50.0/24,dhcpstart=192.168.50.20,hostfwd=tcp:127.0.0.1:9445-192.168.50.20:445,id=nd1 -device rtl8139,netdev=nd1 -drive format=raw,if=ide,file.label=wip,file=fat:rw:"$BASE/wip"