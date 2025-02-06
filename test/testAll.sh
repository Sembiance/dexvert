#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#  1m  4s
dra testMany.js --format=font		#  3m  2s
dra testMany.js --format=other		#  5m 37s
dra testMany.js --format=video		# 22m  2s
dra testMany.js --format=audio		# 25m 25s
dra testMany.js --format=document	# 28m 51s
dra testMany.js --format=text		# 31m 15s
dra testMany.js --format=poly		# 34m 39s?
dra testMany.js --format=music		# 41m 11s?
dra testMany.js --format=archive	# 78m 33s?
dra testMany.js --format=image		# 85m 31s

# dra testMany.js --format=all  #  4h 38m 30s   to  5h 40m 43s		(Last run: 5h 19m 10s)
