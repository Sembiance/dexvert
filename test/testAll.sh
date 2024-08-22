#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     27s
dra testMany.js --format=font		#  3m  9s
dra testMany.js --format=other		#  4m  1s
dra testMany.js --format=text		#  9m 29s
dra testMany.js --format=video		# 17m 16s
dra testMany.js --format=audio		# 17m 28s
dra testMany.js --format=poly		# 25m 23s
dra testMany.js --format=music		# 42m 46s
dra testMany.js --format=document	# 41m 51s
dra testMany.js --format=image		# 53m 35s
dra testMany.js --format=archive	# 69m 50s

# dra testMany.js --format=all		#  3h  53m 19s
