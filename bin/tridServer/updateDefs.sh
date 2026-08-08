#!/bin/bash

wget "https://mark0.net/download/triddefs.zip"
mv triddefs.trd old-triddefs.trd
unzip triddefs.zip
rm triddefs.zip
rm -f .triddefs.trd.cache
