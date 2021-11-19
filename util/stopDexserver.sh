#!/bin/bash
kill -SIGTERM `cat /mnt/ram/dexvert/dexserver.pid`
killall --wait vsftpd
