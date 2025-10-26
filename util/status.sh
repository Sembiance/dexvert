#!/bin/bash

curl --silent 'http://127.0.0.1:17735/status' | jq
curl --silent 'http://127.0.0.1:17750/status' | jq
curl --silent 'http://127.0.0.1:17738/status?verbose=1' | jq
