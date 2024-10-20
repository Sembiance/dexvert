#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     32s
dra testMany.js --format=font		#  7m  3s
dra testMany.js --format=other		#  5m 41s
dra testMany.js --format=text		# 18m 12s
dra testMany.js --format=video		# 17m 54s
dra testMany.js --format=audio		# 22m 45s
dra testMany.js --format=poly		# 28m 22s?
dra testMany.js --format=document	# 33m 51s
dra testMany.js --format=music		# 43m 20s
dra testMany.js --format=image		# 68m 23s
dra testMany.js --format=archive	# 92m  7s

# dra testMany.js --format=all		#  5h 55m 55s?
