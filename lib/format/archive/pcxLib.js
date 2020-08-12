"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "PCXlib Compressed Archive",
	website : "http://fileformats.archiveteam.org/wiki/PCX_Library",
	ext     : [".pcl"],
	magic   : ["pcxLib compressed", "PCX Library game data container"]
};

exports.steps = [(state, p) => p.util.wine.run({cmd : "unpcxgx.exe", args : path.join(state.cwd, state.input.filePath), cwd : state.output.absolute})];
