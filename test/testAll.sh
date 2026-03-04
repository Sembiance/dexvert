#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     38s
dra testMany.js --format=font		#  1m 55s
dra testMany.js --format=other		#  2m 36s


dra testMany.js --format=archive	# 45m 48s
dra testMany.js --format=image		# 46m 55s



dra testMany.js --format=video		# 22m 21s
dra testMany.js --format=audio		# 25m 44s
dra testMany.js --format=document	# 30m 52s
dra testMany.js --format=text		# 39m  3s
dra testMany.js --format=music		# 43m 32s
dra testMany.js --format=poly		# 51m 23s

# dra testMany.js --format=all  #  4h 38m 30s   to  6h 5m 42s   (Last: 5h 43m 10s)
