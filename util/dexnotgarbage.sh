#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: dexNotGarbage <dir>"
    exit
fi

tmpDirPath="/mnt/ram/tmp/"$(tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w 32 | head -n 1)

mkdir "$tmpDirPath"

cd "$1" || exit
for f in *; do
	deno run --v8-flags=--max-old-space-size=32768,--enable-experimental-regexp-engine-on-excessive-backtracks --import-map /mnt/compendium/DevLab/deno/importMap.json --no-check --no-config --unstable --allow-read --allow-write --allow-run --allow-env /mnt/compendium/DevLab/dexvert/util/tensorPreProcess.js "$f" "$tmpDirPath"
done

cd "$tmpDirPath" || exit
renameRandom ./*
fdupes --delete --noprompt .
mv -vf ./* /mnt/compendium/DevLab/dexvert/tensor/garbage/new/notGarbage/

cd ~ || exit
rm -rf "$tmpDirPath"
