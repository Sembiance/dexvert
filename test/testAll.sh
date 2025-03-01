#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#  1m  8s
dra testMany.js --format=font		#  2m 57s
dra testMany.js --format=other		#  7m 36s
dra testMany.js --format=video		# 22m 44s
dra testMany.js --format=audio		# 27m 45s
dra testMany.js --format=document	# 30m 33s
dra testMany.js --format=text		# 31m 53s
dra testMany.js --format=poly		# 40m 38s
dra testMany.js --format=music		# 44m 25s
dra testMany.js --format=archive	# 79m 55s
dra testMany.js --format=image		# 86m  2s

# dra testMany.js --format=all  #  4h 38m 30s   to  5h 40m 43s		(Last run: 5h 21m 31s)
