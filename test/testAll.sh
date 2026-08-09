#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     34s
dra testMany.js --format=font		#  1m 55s
dra testMany.js --format=other		#  2m 32s
dra testMany.js --format=poly		#  9m 42s
dra testMany.js --format=audio		# 14m 35s
dra testMany.js --format=video		# 16m  1s
dra testMany.js --format=text		# 16m 29s
dra testMany.js --format=music		# 22m 25s
dra testMany.js --format=document	# 25m 46s
dra testMany.js --format=image		# 42m 58s
dra testMany.js --format=archive	# 43m 10s

# dra testMany.js --format=all  #  3h 48m 26s
