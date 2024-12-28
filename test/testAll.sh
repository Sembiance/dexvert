#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#  1m  1s
dra testMany.js --format=other		#  6m 42s
dra testMany.js --format=font		#  7m  3s?
dra testMany.js --format=video		# 21m 55s?
dra testMany.js --format=audio		# 24m  3s?
dra testMany.js --format=text		# 26m 54s?
dra testMany.js --format=document	# 28m 48s?
dra testMany.js --format=poly		# 34m 39s
dra testMany.js --format=music		# 41m 11s?
dra testMany.js --format=image		# 78m 34s
dra testMany.js --format=archive	# 78m 35s?

# dra testMany.js --format=all  #  4h 38m 30s   to  5h 40m 43s
