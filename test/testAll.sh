#!/bin/bash

shopt -s expand_aliases
source /etc/bash/bashrc.d/bash_aliases

# times are from ridgeport Dec 25, 2023

dra testMany.js --format=poly		#     38s
dra testMany.js --format=executable	#  1m 11s
dra testMany.js --format=text		#  1m 18s
dra testMany.js --format=font		#  1m 29s
dra testMany.js --format=other		#  2m 35s
dra testMany.js --format=video		# 10m 27s
dra testMany.js --format=audio		# 11m 32s
dra testMany.js --format=music		# 20m 28s
dra testMany.js --format=document	# 20m 45s
dra testMany.js --format=archive	# 30m 38s
dra testMany.js --format=image		# 36m 34s
