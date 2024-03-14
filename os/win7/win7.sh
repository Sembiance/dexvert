#!/bin/bash

#  CD ISO: -drive file=/mnt/compendium/DevLab/dexvert/aux/win7/GSP1RMCPRXFRER_EN_DVD.ISO,if=ide,media=cdrom
# For a CD-ROM for booting, set -boot order=dc
# WIP dir: -drive format=raw,if=ide,file.label=wip,file=fat:rw:"$BASE/wip"
# -vnc :14
qemu-system-x86_64 -nodefaults -machine accel=kvm,dump-guest-core=off -rtc base="2023-03-01T10:00:00" -device virtio-rng-pci -m size=16G -smp cores=4 -vga cirrus -drive format=qcow2,if=ide,index=0,file=hd.qcow2 -boot order=c -netdev user,net=192.168.51.0/24,dhcpstart=192.168.51.20,id=nd1 -device rtl8139,netdev=nd1 -drive if=floppy,media=disk
