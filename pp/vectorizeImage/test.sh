#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export OUR_DIR="$SCRIPT_DIR"
export VIRTUAL_ENV="$OUR_DIR/env"
export HOME="$OUR_DIR/home"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia/cublas/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/torch/lib:$LD_LIBRARY_PATH"
export PATH="$VIRTUAL_ENV/bin:/opt/cuda/bin:$PATH"
export CUDA_VISIBLE_DEVICES="0"

rm -rf /mnt/ram/tmp/vectorizeImageTest
mkdir -p /mnt/ram/tmp/vectorizeImageTest/original /mnt/ram/tmp/vectorizeImageTest/prepared
cp "$OUR_DIR/sample/0242picx.gif" /mnt/ram/tmp/vectorizeImageTest/original

python3 vectorizeImagePreProcess.py /mnt/ram/tmp/vectorizeImageTest/original /mnt/ram/tmp/vectorizeImageTest/prepared

sleep 1

python3 vectorizeImageServer.py --web_port 33004 &
vectorizeServerPID=$!
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

result=$(curl -s -X POST -H "Content-Type: application/json" -d '{"filePaths":["/mnt/ram/tmp/vectorizeImageTest/prepared/0242picx.gif"]}' "http://127.0.0.1:33004/process" | jq '.[0] | length')
if [[ "$result" -eq 768 ]]; then
	echo "✓ PASS: Got expected value $result"
else
	echo "╳ FAIL: Expected 768 numbers, got $result"
fi

kill $vectorizeServerPID
wait

