#!/bin/bash

#  CD ISO: -drive file=/mnt/compendium/DevLab/dexvert/aux/win7/en_windows_7_AIO_sp1_x64_x86_dvd.ISO,if=ide,media=cdrom
# For a CD-ROM for booting, set -boot order=dc
# WIP dir: -drive format=raw,if=ide,file.label=wip,file=fat:rw:"$BASE/wip"
# -vnc :14
qemu-system-x86_64 -nodefaults -machine accel=kvm,dump-guest-core=off -cpu host -rtc base="2026-03-03T07:12:00" -device virtio-rng-pci -m size=3G -smp cores=2 -vga std -usb -device usb-tablet -drive format=qcow2,if=virtio,file=hd.qcow2,cache=writeback,aio=threads,discard=unmap -boot order=c -netdev user,net=192.168.51.0/24,dhcpstart=192.168.51.20,id=nd1 -device virtio-net-pci,netdev=nd1 -drive if=floppy,media=disk -drive id=cd0,if=none,media=cdrom,readonly=on -device ide-cd,drive=cd0 -monitor unix:/tmp/qemu-monitor.sock,server,nowait
