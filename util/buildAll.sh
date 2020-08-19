#!/bin/bash

node buildReadme.js &
node buildSupportedAndUnsupported.js &

wait
