#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export OUR_DIR="$SCRIPT_DIR"
export VIRTUAL_ENV="$OUR_DIR/env"
export HOME="$OUR_DIR/home"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/nvidia/cublas/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/torch/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$VIRTUAL_ENV/lib/python3.12/site-packages/torchaudio/lib:$LD_LIBRARY_PATH"
export PATH="$VIRTUAL_ENV/bin:/opt/cuda/bin:$PATH"
export CUDA_VISIBLE_DEVICES="0"

rm -rf /mnt/ram/tmp/vectorizeAudioTest
mkdir -p /mnt/ram/tmp/vectorizeAudioTest/original /mnt/ram/tmp/vectorizeAudioTest/prepared
cp "$OUR_DIR/sample/00012312.mp3" /mnt/ram/tmp/vectorizeAudioTest/original

python3 vectorizeAudioPreProcess.py /mnt/ram/tmp/vectorizeAudioTest/original /mnt/ram/tmp/vectorizeAudioTest/prepared

sleep 1

python3 vectorizeAudioServer.py --web_port 33004 &
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

result=$(curl -s -X POST -H "Content-Type: application/json" -d '{"filePaths":["/mnt/ram/tmp/vectorizeAudioTest/prepared/00012312.mp3"]}' "http://127.0.0.1:33004/process" | jq '.[0] | length')
if [[ "$result" -eq 512 ]]; then
	echo "✓ PASS: Got expected value $result"
else
	echo "╳ FAIL: Expected 512 numbers, got $result"
fi

kill $vectorizeServerPID
wait

