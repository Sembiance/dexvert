#!/bin/bash
echo "change floppy0 \"$(realpath "$1")\"" | socat - UNIX-CONNECT:/tmp/qemu-monitor.sock
