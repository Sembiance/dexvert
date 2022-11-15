#!/usr/bin/env python3

# inspired by: https://github.com/asiekierka/zzt-toolbox/blob/master/screenshot_grab.py

import math, os, re, sys, pathlib
sys.path.append(pathlib.Path(__file__).parent.resolve())
import zookeeper

def main():
	zoo = zookeeper.Zookeeper()
	zoo.load_file(sys.argv[1])
	zoo.parse_file()
	for idx, board in enumerate(zoo.boards):
		img = board.render(title_screen=(True if idx == 0 else False))
		fnFormat = "%s %0" + str(len(str(len(zoo.boards)))) + "d: %s"
		fn = os.path.join(sys.argv[2], fnFormat % (zoo.world._world_name, idx, re.sub("[/]", "⁄", board.title)))
		img.save(fn, "PNG")

if __name__ == "__main__":
	main()
