#!/bin/bash

shopt -s expand_aliases
source /etc/bash/bashrc.d/bash_aliases

# col1 times are from dexdrone1 Feb 17, 2024
# col2 times are from dexdrone1 Apr 01, 2024

dra testMany.js --format=executable	#     25s        29s
dra testMany.js --format=poly		#     44s    ??m ??s
dra testMany.js --format=font		#  1m 25s    ??m ??s
dra testMany.js --format=other		#  2m  0s    ??m ??s
dra testMany.js --format=text		#  2m  9s    ??m ??s
dra testMany.js --format=video		# 15m 54s    ??m ??s
dra testMany.js --format=audio		# 18m 34s    ??m ??s
dra testMany.js --format=music		# 23m 28s    ??m ??s
dra testMany.js --format=document	# 26m 34s    ??m ??s
dra testMany.js --format=image		# 37m 10s    ??m ??s
dra testMany.js --format=archive	# 37m 20s    ??m ??s

#   TOTAL TIME RUNNING ALL AT ONCE: # 