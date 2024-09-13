#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     34s
dra testMany.js --format=other		#  3m 22s
dra testMany.js --format=font		#  7m 31s
dra testMany.js --format=text		# 11m  8s
dra testMany.js --format=video		# 14m 38s
dra testMany.js --format=audio		# 16m 26s
dra testMany.js --format=poly		# 25m 23s
dra testMany.js --format=document	# 27m 57s
dra testMany.js --format=music		# 38m 50s
dra testMany.js --format=image		# 65m 32s
dra testMany.js --format=archive	# 78m 34s

# dra testMany.js --format=all		#  3h  53m 19s
