#!/bin/bash
mkdir -p ftp
echo "You can use this to transfer files to/from amiga"
echo "Stick files you want to serve in the 'ftp' dir"
echo "On the amiga side do:"
echo "  ftp"
echo "  open 192.168.52.2 7021"
echo "  anonymous"
echo "  passive"

uftpd -l info -n -o ftp=7021,pasv_addr=192.168.52.2,writable ftp
