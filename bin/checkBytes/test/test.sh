#!/bin/bash

for type in "Printable ASCII" "All Null Bytes" "Null Bytes Alternating" "All Identical Bytes" "nothing"
do
	for f in ./"$type"/*
	do
		result=$(../checkBytes "$f")
		if [[ "$type" == "nothing" && "$result" != "" ]] || [[ "$type" != "nothing" && "$result" != "$type" ]]; then
			echo "File $f does not match expected!"
		fi
	done
done

echo "Test complete"
