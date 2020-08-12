"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "Genus Graphics Library Compressed Archive",
	website : "http://fileformats.archiveteam.org/wiki/Genus_Graphics_Library",
	ext     : [".gx", ".gxl"],
	magic   : ["Genus Graphics Library"]
};

exports.steps = [(state, p) => p.util.wine.run({cmd : "unpcxgx.exe", args : path.join(state.cwd, state.input.filePath), cwd : state.output.absolute})];
