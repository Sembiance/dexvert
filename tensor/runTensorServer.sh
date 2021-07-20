#!/bin/bash

TPATH="/mnt/ram/dexvert/tensor"

echo "Removing existing tensor dir..."
rm -rf "$TPATH"

echo "Creating tensor dir..."
mkdir -p "$TPATH"/garbage "$TPATH"/__pycache__ "$TPATH"/tmp

echo "Changing dir and copying over tensor files..."
cd /mnt/compendium/DevLab/dexvert/tensor || exit
cp tensorServer.sh ./*.py "$TPATH"/
cp -rv garbage/model "$TPATH"/garbage/

cd "$TPATH" || exit

echo "Running tensor docker..."
docker run -d --name dexvert-tensor --gpus all -it --rm -p 17736:17736 -v "$TPATH":"$TPATH" -w "$TPATH" tensorflow/tensorflow:latest-gpu ./tensorServer.sh

function clean_up
{
	echo "Signal caught. Stopping docker container..."
	docker stop dexvert-tensor

	echo "Tensor children done."
	exit 1
}

trap clean_up SIGTERM

docker wait dexvert-tensor &
wait
