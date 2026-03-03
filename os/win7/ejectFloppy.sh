#!/bin/bash
echo "eject floppy0" | socat - UNIX-CONNECT:/tmp/qemu-monitor.sock