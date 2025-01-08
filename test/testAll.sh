#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

                                    # intel          # amd
dra testMany.js --format=executable	#  1m  1s		     52s
dra testMany.js --format=other		#  6m 42s		  7m 18s
dra testMany.js --format=font		#  7m  3s		  6m 35s
dra testMany.js --format=video		# 21m 55s		 10m 07s
dra testMany.js --format=audio		# 24m  3s		 15m 19s
dra testMany.js --format=text		# 26m 54s		 16m 48s
dra testMany.js --format=document	# 28m 48s		 15m 15s
dra testMany.js --format=poly		# 34m 39s		 24m 58s
dra testMany.js --format=music		# 41m 11s		 20m 35s
dra testMany.js --format=archive	# 78m 35s		 47m 15s
dra testMany.js --format=image		# 78m 34s		 57m 06s

# dra testMany.js --format=all  #  4h 38m 30s   to  5h 40m 43s		(Last run: 5h 19m 10s)
