#!/bin/bash

shopt -s expand_aliases
source /etc/bash/bashrc.d/bash_aliases

# col1 times are from ridgeport Dec 25, 2023
# col2 times are from dexdrone1 Jan 22, 2024

dra testMany.js --format=poly		#     38s	    47s
dra testMany.js --format=executable	#  1m 11s	    25s
dra testMany.js --format=text		#  1m 18s	 1m 44s
dra testMany.js --format=font		#  1m 29s	 1m 33s
dra testMany.js --format=other		#  2m 35s	 2m 19s
dra testMany.js --format=video		# 10m 27s
dra testMany.js --format=audio		# 11m 32s
dra testMany.js --format=music		# 20m 28s
dra testMany.js --format=document	# 20m 45s
dra testMany.js --format=archive	# 30m 38s
dra testMany.js --format=image		# 36m 34s
