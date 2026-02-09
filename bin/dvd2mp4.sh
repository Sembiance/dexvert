#!/bin/bash
set -euo pipefail

max_jobs=$(( $(nproc) / 4 )); (( max_jobs < 1 )) && max_jobs=1
scan=$(HandBrakeCLI -i "$1" -t 0 --json --scan 2>/dev/null | sed -n '/^JSON Title Set: /,$ p' | sed '1s/^JSON Title Set: //')
while read -r t; do
    outfile="$2/title_$(printf '%02d' "$t").mp4"
    echo "=== Encoding title $t → $outfile ==="

    HandBrakeCLI -i "$1" -t "$t" -e nvenc_h264 -q 22 --encoder-preset p5 --comb-detect --decomb -E aac -B 256 --mixdown stereo --optimize --markers -o "$outfile" </dev/null &
    while (( $(jobs -r | wc -l) >= max_jobs )); do
        sleep 1
    done
done < <(echo "$scan" | jq -r '.TitleList[].Index')

wait
echo "=== Done ==="
