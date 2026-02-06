#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export OUR_DIR="$SCRIPT_DIR"
export VIRTUAL_ENV="$OUR_DIR/env"
export HOME="$OUR_DIR/home"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/tensorrt_libs:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/tensorrt_bindings:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/tensorrt:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/torch/lib:$LD_LIBRARY_PATH"
export PATH="$VIRTUAL_ENV/bin:/opt/cuda/bin:$PATH"
export CUDA_VISIBLE_DEVICES="0"

rm -rf /mnt/ram/tmp/ocrTest
mkdir -p /mnt/ram/tmp/ocrTest/original /mnt/ram/tmp/ocrTest/prepared
magick "$OUR_DIR/sample/0242picx.gif" /mnt/ram/tmp/ocrTest/original/0242picx.png

python3 ocrPreProcess.py /mnt/ram/tmp/ocrTest/original /mnt/ram/tmp/ocrTest/prepared

sleep 1

python3 ocrServer.py --web_port 33004 &
ocrServerPID=$!
sleep 4

while true; do
	response=$(curl -s "http://127.0.0.1:33004/status" | grep "a-ok")
	if [ "$response" != "" ]; then
		break
	else
		echo "Waiting for server to start..."
		sleep 1
	fi
done

result=$(curl -s -X POST -H "Content-Type: application/json" -d '{"filePaths":["/mnt/ram/tmp/ocrTest/prepared/0242picx.png.npy"]}' "http://127.0.0.1:33004/process" | jq -r '.[0].pages[].blocks[].lines[].words[].value')
if echo "$result" | grep -q "Image" && echo "$result" | grep -q "Center"; then
    echo "✓ PASS: Found 'Image' and 'Center' with result: $result"
else
    echo "╳ FAIL: Expected words not found: $result"
fi

kill $ocrServerPID
wait

