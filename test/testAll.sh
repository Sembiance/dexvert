#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#  1m  5s
dra testMany.js --format=font		#  2m 56s
dra testMany.js --format=other		#  5m 22s
dra testMany.js --format=video		# 20m 49s
dra testMany.js --format=audio		# 27m 58s
dra testMany.js --format=document	# 29m 14s
dra testMany.js --format=text		# 34m 10s
dra testMany.js --format=music		# 43m 51s
dra testMany.js --format=poly		# 48m 31s
dra testMany.js --format=archive	# 70m 31s
dra testMany.js --format=image		# 84m 51s

# dra testMany.js --format=all  #  4h 38m 30s   to  5h 40m 43s		(Last run: 5h 53m 29s)
