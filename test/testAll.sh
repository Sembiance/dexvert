#!/bin/bash

shopt -s expand_aliases
source /etc/bash/bashrc.d/bash_aliases

# col1 times are from ridgeport Dec 25, 2023
# col2 times are from dexdrone1 Jan 22, 2024
# col3 times are from dexdrone1 Feb 17, 2024

dra testMany.js --format=executable	#  1m 11s	    23s		    28s
dra testMany.js --format=poly		#     38s	    48s		    44s
dra testMany.js --format=font		#  1m 29s	 1m 22s		 1m 28s
dra testMany.js --format=other		#  2m 35s	 2m 30s		 2m  0s
dra testMany.js --format=text		#  1m 18s	 1m 19s		 2m  9s
dra testMany.js --format=video		# 10m 27s	11m 59s		15m 54s
dra testMany.js --format=audio		# 11m 32s	14m 22s		18m 34s
dra testMany.js --format=music		# 20m 28s	24m 17s		??m ??s
dra testMany.js --format=document	# 20m 45s	26m 44s		??m ??s
dra testMany.js --format=archive	# 30m 38s	41m  5s		??m ??s
dra testMany.js --format=image		# 36m 34s	36m  3s		??m ??s
