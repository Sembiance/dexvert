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

rm -rf /mnt/ram/tmp/transcribeTest
mkdir -p /mnt/ram/tmp/transcribeTest/original /mnt/ram/tmp/transcribeTest/prepared
cp "$OUR_DIR/sample/d052104u.mp3" /mnt/ram/tmp/transcribeTest/d052104u.mp3

python3 transcribeServer.py --web_port 33004 &
transcribeServerPID=$!
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

curl -s -X POST -H "Content-Type: application/json" -d '{"filePaths":["/mnt/ram/tmp/transcribeTest/d052104u.mp3"]}' "http://127.0.0.1:33004/process" | jq | head -n 1
result=$(curl -s -X POST -H "Content-Type: application/json" -d '{"filePaths":["/mnt/ram/tmp/transcribeTest/d052104u.mp3"]}' "http://127.0.0.1:33004/process" | jq '.[0][0].text')
if [[ "$result" == *"You seem to spend a lot of time talking"* ]]; then
	echo "✓ PASS: Got expected value $result"
else
	echo "╳ FAIL: Not what was expected, got $result"
fi

kill $transcribeServerPID
wait

