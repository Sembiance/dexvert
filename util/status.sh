#!/bin/bash

curl 'http://127.0.0.1:17735/status' | jq
curl 'http://127.0.0.1:17750/status' | jq

