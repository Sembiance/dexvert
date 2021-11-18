#!/bin/bash

cd /mnt/dexvert/qemu || exit
for f in *; do
	sudo umount -l "$f"/in
	sudo umount -l "$f"/out
done
