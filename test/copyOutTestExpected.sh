#!/bin/bash

if [[ $(hostname) == "crystalsummit" ]]; then
	ssh sembiance@cobbleton-public "scp dexvert:/mnt/compendium/DevLab/dexvert/test/testExpected.json /mnt/compendium/DevLab/dexvert/test/"
	scp sembiance@cobbleton-public:/mnt/compendium/DevLab/dexvert/test/testExpected.json /mnt/compendium/DevLab/dexvert/test/
else
	scp dexvert:/mnt/compendium/DevLab/dexvert/test/testExpected.json /mnt/compendium/DevLab/dexvert/test/
fi
