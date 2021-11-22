#!/bin/bash
cd "$(dirname "$0")" || exit
./buildFormats "$@"
./buildPrograms "$@"
