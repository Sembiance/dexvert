#!/bin/bash
echo "eject cd0" | socat - UNIX-CONNECT:/tmp/qemu-monitor.sock

