#!/bin/bash

node buildReadme.js &
node buildSupported.js &
node buildUnsupported.js &

wait
