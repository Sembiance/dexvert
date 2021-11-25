#!/bin/bash
cd "$(dirname "$0")" || exit
./buildPrograms "$@"
./buildFormats "$@"
