#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     23s
dra testMany.js --format=font		#  2m 16s
dra testMany.js --format=other		#  3m  1s
dra testMany.js --format=text		#  7m 34s
dra testMany.js --format=audio		# 15m 54s
dra testMany.js --format=video		# 16m 43s
dra testMany.js --format=poly		# 21m 33s
dra testMany.js --format=music		# 42m 46s
dra testMany.js --format=document	# 41m 51s
dra testMany.js --format=image		# 53m 35s
dra testMany.js --format=archive	# 86m 56s

# dra testMany.js --format=all		#  3h  53m 19s
