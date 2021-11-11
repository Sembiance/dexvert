#!/bin/bash

TPATH="/mnt/ram/dexvert/tensor"
cd "$TPATH"  || exit

pip install flask pillow
python -X pycache_prefix="$TPATH"/__pycache__ tensorServer.py
