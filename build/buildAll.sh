#!/bin/bash
cd `dirname $0`
./buildFormats "$@"
./buildPrograms "$@"
