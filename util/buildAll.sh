#!/bin/bash

node buildReadme.js &
node buildSupportedAndUnsupported.js &
node buildInstall.js &

wait
