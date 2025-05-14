#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#  1m 00s
dra testMany.js --format=font		#  3m 05s
dra testMany.js --format=other		#  5m 43s
dra testMany.js --format=video		# 24m 57s
dra testMany.js --format=audio		# 27m 20s
dra testMany.js --format=document	# 30m 13s
dra testMany.js --format=text		# 36m 26s
dra testMany.js --format=music		# 45m 22s
dra testMany.js --format=poly		# 50m 35s
dra testMany.js --format=archive	# 70m 46s
dra testMany.js --format=image		# 82m 58s

# dra testMany.js --format=all  #  4h 38m 30s   to  6h 5m 42s
