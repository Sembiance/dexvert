#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#  1m  5s
dra testMany.js --format=font		#  3m 31s
dra testMany.js --format=other		#  5m 33s
dra testMany.js --format=video		# 22m 25s
dra testMany.js --format=audio		# 28m 57s
dra testMany.js --format=document	# 30m 33s
dra testMany.js --format=text		# 31m 53s
dra testMany.js --format=poly		# 40m 38s
dra testMany.js --format=music		# 45m 18s
dra testMany.js --format=archive	# 73m 33s
dra testMany.js --format=image		# 86m 52s

# dra testMany.js --format=all  #  4h 38m 30s   to  5h 40m 43s		(Last run: 5h 53m 29s)
