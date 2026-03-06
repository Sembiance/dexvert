#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     38s
dra testMany.js --format=font		#  1m 55s
dra testMany.js --format=other		#  2m 36s
dra testMany.js --format=video		# 14m 55s
dra testMany.js --format=audio		# 18m 46s
dra testMany.js --format=text		# 19m  1s
dra testMany.js --format=document	# 20m 43s
dra testMany.js --format=music		# 20m 45s
dra testMany.js --format=poly		# 34m 41s
dra testMany.js --format=archive	# 44m 30s
dra testMany.js --format=image		# 50m 21s

# dra testMany.js --format=all  #  3h 29m 25s
