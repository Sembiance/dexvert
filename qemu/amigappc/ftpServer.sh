#!/bin/bash
mkdir -p /mnt/ram/dexvert/ftp/in /mnt/ram/dexvert/ftp/out /mnt/ram/dexvert/ftp/backup
echo "Starting UFTPD for dir: /mnt/ram/dexvert/ftp/"
uftpd -l info -n -o ftp=7021,pasv_addr=192.168.52.2,writable /mnt/ram/dexvert/ftp
