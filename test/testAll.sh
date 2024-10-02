#!/bin/bash

shopt -s expand_aliases
source /mnt/compendium/sys/bash/bash_aliases

dra testMany.js --format=executable	#     33s
dra testMany.js --format=other		#  4m 11s
dra testMany.js --format=font		#  7m 14s?
dra testMany.js --format=video		# 14m  7s?
dra testMany.js --format=text		# 14m 52s?
dra testMany.js --format=audio		# 16m 21s?
dra testMany.js --format=document	# 25m  9s?
dra testMany.js --format=poly		# 25m 45s?
dra testMany.js --format=music		# 39m  3s?
dra testMany.js --format=image		# 65m 27s
dra testMany.js --format=archive	# 84m 57s

# dra testMany.js --format=all		#  5h 55m 55s?
