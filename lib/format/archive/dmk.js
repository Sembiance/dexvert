"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "TRS-80 Disk Image",
	website : "http://fileformats.archiveteam.org/wiki/DMK",
	ext     : [".dmk", ".dsk"],
	magic   : ["TRS-80 DMK"]
};

exports.steps = [(state, p) => p.util.wine.run({cmd : "trsread.exe", args : ["-e", "-s", "-i", "-i", path.join(state.cwd, state.input.filePath)], cwd : state.output.absolute})];
