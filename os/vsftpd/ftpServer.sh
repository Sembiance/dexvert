#!/bin/bash
mkdir -p /mnt/ram/tmp/dexvert-ftp
echo "Starting VSFTPD for dir: /mnt/ram/tmp/dexvert-ftp/"
vsftpd /mnt/compendium/DevLab/dexvert/os/vsftpd/vsftpd-qemu.conf
