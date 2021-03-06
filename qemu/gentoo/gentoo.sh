#!/bin/bash
BASE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$BASE" || exit

#  CD ISO: -drive file=data/install-amd64-minimal-20210602T214502Z.iso,media=cdrom
# WIP dir: -drive format=raw,if=ide,file.label=wip,file=fat:rw:"$BASE/wip"
# -vnc :14
qemu-system-x86_64 -machine accel=kvm,dump-guest-core=off -drive format=raw,file=hd.img,if=virtio -device virtio-rng-pci -m size=32G -smp cores=8 -boot order=c -netdev user,net=192.168.53.0/24,dhcpstart=192.168.53.20,hostfwd=tcp:127.0.0.1:57022-192.168.53.20:22,id=nd1 -device virtio-net,netdev=nd1 -drive if=pflash,format=raw,unit=0,file=/usr/share/edk2-ovmf/OVMF_CODE.fd,readonly=on -drive if=pflash,format=raw,unit=1,file=OVMF_VARS.fd -drive format=raw,file=extra.img,if=virtio -drive format=raw,file=var_tmp.img,if=virtio