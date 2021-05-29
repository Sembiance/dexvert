#!/bin/bash
mkdir -p /mnt/ram/dexvert/ftp/in /mnt/ram/dexvert/ftp/out /mnt/ram/dexvert/ftp/backup
echo "Starting VSFTPD for dir: /mnt/ram/dexvert/ftp/"
vsftpd /mnt/compendium/DevLab/dexvert/ftp/amigappc-vsftpd.conf
