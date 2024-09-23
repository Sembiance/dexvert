#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     26s
dra testMany.js --format=other		#  3m 30s
dra testMany.js --format=font		#  7m 38s
dra testMany.js --format=text		# 12m 36s
dra testMany.js --format=video		# 14m 14s
dra testMany.js --format=audio		# 16m 21s
dra testMany.js --format=document	# 25m  9s
dra testMany.js --format=poly		# 25m 45s
dra testMany.js --format=music		# 39m  3s
dra testMany.js --format=image		# 58m 46s
dra testMany.js --format=archive	# 99m 34s

# dra testMany.js --format=all		#  3h  53m 19s?
