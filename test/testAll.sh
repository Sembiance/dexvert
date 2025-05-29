#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#  1m  6s
dra testMany.js --format=font		#  3m 36s
dra testMany.js --format=other		#  5m 35s?
dra testMany.js --format=video		# 24m 19s?
dra testMany.js --format=audio		# 27m 20s?
dra testMany.js --format=document	# 30m 13s?
dra testMany.js --format=text		# 35m  4s?
dra testMany.js --format=music		# 42m 10s?
dra testMany.js --format=poly		# 50m 46s?
dra testMany.js --format=archive	# 74m 50s?
dra testMany.js --format=image		# 88m 59s?

# dra testMany.js --format=all  #  4h 38m 30s   to  6h 5m 42s   (Last: 5h 35m 42s)
