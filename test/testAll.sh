#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

# col1 times are from dexdrone1 Feb 17, 2024
# col2 times are from dexdrone1 Apr 01, 2024
# col3 times are from dexdrone1 Jun 17, 2024

dra testMany.js --format=executable	#     25s        25s	    29s
dra testMany.js --format=font		#  1m 25s     1m 45s	 1m 49s
dra testMany.js --format=text		#  2m  9s     1m 50s	 2m  6s
dra testMany.js --format=other		#  2m  0s     2m 36s	 3m 13s
dra testMany.js --format=video		# 15m 54s    11m 51s	14m 58s
dra testMany.js --format=poly		#     44s    16m 10s	20m 44s
dra testMany.js --format=audio		# 18m 34s    20m 39s	20m 18s?
dra testMany.js --format=document	# 26m 34s    27m 56s	34m 49s?
dra testMany.js --format=music		# 23m 28s    24m 10s	35m 57s?
dra testMany.js --format=image		# 37m 10s    38m 49s	52m  6s?
dra testMany.js --format=archive	# 37m 20s    43m 31s	72m 52s?
