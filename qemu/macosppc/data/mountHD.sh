#!/bin/bash
BASE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$BASE" || exit
mount_afp afp://dexvert:dexvert@127.0.0.1:9548/hd hd
