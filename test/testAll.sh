#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     25s
dra testMany.js --format=other		#  6m  7s
dra testMany.js --format=font		#  7m 22s
dra testMany.js --format=video		# 17m 26s
dra testMany.js --format=text		# 18m 43s
dra testMany.js --format=audio		# 26m 42s
dra testMany.js --format=document	# 28m  4s
dra testMany.js --format=poly		# 31m 24s
dra testMany.js --format=music		# 41m 11s
dra testMany.js --format=image		# 69m  2s
dra testMany.js --format=archive	# 78m 32s

# dra testMany.js --format=all  #  4h 52m 30s
