#!/bin/bash

TESTIDS_PATH="/mnt/ram/tmp/testids.txt"
TESTIDS_SKIPPED_PATH="/mnt/ram/tmp/testids_SKIPPED.txt"

if [ ! -f "$TESTIDS_PATH" ]; then
	echo ">>> Find the formats you want to identify:"
	echo "cd test/sample"
	echo "find ./image -maxdepth 2 -type f > $TESTIDS_PATH"
	echo ""
	echo ">>> Now open /tmp/testids.txt in vscode and run regex: "
	echo '   Find: ^\./([^/]+/[^/]+)/([^\n]+)\n'
	echo 'Replace: $1\n$2\n'
	echo ""
	echo ">>> Ensure there is a newline at the end of the file"
	echo ">>> Now run the util/testids.sh script"

	exit
fi

cd /mnt/compendium/DevLab/dexvert/test || exit

while :
do
	format=$(sed -n '1p' $TESTIDS_PATH)
	filename=$(sed -n '2p' $TESTIDS_PATH)

	echo "Format [${format}] and file: ${filename}"
	./testid --quiet --format="$format" --file="$filename"

	read -s -p "R to retry   S to save   N to skip   Q to quit" -n1 charAnswer
	echo "";

	if [ "$charAnswer" = "q" ]; then
		echo "Exiting..."
		exit
	fi
	if [ "$charAnswer" = "s" ]; then
		./testid --quiet --format="$format" --file="$filename" --record
		sed -i '1d' "$TESTIDS_PATH"
		sed -i '1d' "$TESTIDS_PATH"
		continue
	fi
	if [ "$charAnswer" = "n" ]; then
		echo "$format" >> "$TESTIDS_SKIPPED_PATH"
		echo "$filename" >> "$TESTIDS_SKIPPED_PATH"
		sed -i '1d' "$TESTIDS_PATH"
		sed -i '1d' "$TESTIDS_PATH"
		continue
	fi
	if [ "$charAnswer" = "r" ]; then
		echo "Retrying..."
		continue;
	fi

	echo "UNKNOWN ANSWER: $charAnswer"
	exit
done
