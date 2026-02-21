#!/usr/bin/env bash
set -euo pipefail

outpath=$(grep -m1 '^begin ' "$1" | awk '{print $3}')
outdir=$(dirname "$outpath")
[[ "$outdir" != "." ]] && mkdir -p "$outdir"
uudecode "$1"
