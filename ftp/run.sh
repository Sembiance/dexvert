#!/bin/bash
mkdir -p /mnt/ram/dexvert/ftp/in
mkdir -p /mnt/ram/dexvert/ftp/out
vsftpd /mnt/compendium/DevLab/dexvert/ftp/amigappc-vsftpd.conf
