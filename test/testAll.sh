#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     30s
dra testMany.js --format=font		#  7m 32s
dra testMany.js --format=other		#  8m 40s
dra testMany.js --format=text		# 16m 38s
dra testMany.js --format=audio		# 19m 21s
dra testMany.js --format=video		# 19m 45s
dra testMany.js --format=document	# 28m 17s
dra testMany.js --format=poly		# 28m 22s
dra testMany.js --format=music		# 41m 29s
dra testMany.js --format=image		# 64m 25s
dra testMany.js --format=archive	# 95m 35s

# dra testMany.js --format=all		#  5h 55m 55s?
