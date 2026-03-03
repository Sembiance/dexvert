#!/bin/bash
echo "change cd0 \"$(realpath "$1")\"" | socat - UNIX-CONNECT:/tmp/qemu-monitor.sock
