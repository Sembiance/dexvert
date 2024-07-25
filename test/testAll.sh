#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     33s
dra testMany.js --format=font		#  2m  6s
dra testMany.js --format=other		#  2m 42s
dra testMany.js --format=text		#  5m 58s
dra testMany.js --format=video		# 14m 17s
dra testMany.js --format=audio		# 16m  1s
dra testMany.js --format=poly		# 19m 20s?
dra testMany.js --format=music		# 38m 46s?
dra testMany.js --format=document	# 43m 15s?
dra testMany.js --format=image		# 55m 33s?
dra testMany.js --format=archive	# 97m 16s?

# dra testMany.js --format=all		#  3h  53m 19s
