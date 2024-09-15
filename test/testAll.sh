#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     31s
dra testMany.js --format=other		#  3m 15s
dra testMany.js --format=font		#  7m 18s
dra testMany.js --format=text		# 12m  0s
dra testMany.js --format=audio		# 16m 52s
dra testMany.js --format=video		# 17m 53s
dra testMany.js --format=poly		# 25m 23s?
dra testMany.js --format=document	# 27m 11s
dra testMany.js --format=music		# 38m 47s
dra testMany.js --format=image		# 56m 22s
dra testMany.js --format=archive	# 68m 30s

# dra testMany.js --format=all		#  3h  53m 19s
