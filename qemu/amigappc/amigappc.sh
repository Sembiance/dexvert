#!/bin/bash
BASE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$BASE" || exit

#  CD ISO: -device ide-cd,drive=cd,bus=ide.1 -drive file=data/Sam460InstallCD-53.58-patched.iso,if=none,id=cd,format=raw
# -vnc :14
qemu-system-ppc -machine type=sam460ex,dump-guest-core=off -rtc base="2021-04-18T10:00:00" -m size=1G -device ide-hd,drive=disk,bus=ide.0 -drive file=hd.img,format=raw,id=disk -netdev user,net=192.168.52.0/24,dhcpstart=192.168.52.20,hostfwd=tcp:127.0.0.1:9139-192.168.52.20:139,id=nd1 -device ne2k_pci,netdev=nd1 -device ES1370
