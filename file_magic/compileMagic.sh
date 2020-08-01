#!/bin/bash

cat dexvert-magic > tmpMagic

for f in /usr/share/misc/magic/*
do
	echo "" >> tmpMagic
	cat "$f" >> tmpMagic
done

command file -C -m tmpMagic

rm tmpMagic
mv tmpMagic.mgc dexvert-magic.mgc
