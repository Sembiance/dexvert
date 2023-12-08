#!/bin/bash

# times are from ridgeport Dec 7, 2023
dra testMany.js --format=audio		# 12m 39s
dra testMany.js --format=document	# 19m 53s
dra testMany.js --format=image		# 25m 35s
dra testMany.js --format=other		#  1m 44s
dra testMany.js --format=font		#  1m 27s
dra testMany.js --format=text		#     52s
dra testMany.js --format=poly		#     39s
dra testMany.js --format=executable	#     30s



dra testMany.js --format=archive
dra testMany.js --format=music
dra testMany.js --format=video
