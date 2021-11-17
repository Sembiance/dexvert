#!/bin/bash
BASE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$BASE" || exit
sudo umount hd
afp_client exit
