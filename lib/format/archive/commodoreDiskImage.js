"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs");

exports.meta =
{
	name    : "Commodore Disk Image",
	website : "http://fileformats.archiveteam.org/wiki/D64",
	ext     : [".d64", ".d81", ".d71"],
	magic   : ["D64 Image", "D81 Image"]
};

exports.steps =
[
	() => (state, p, cb) => fs.symlink(state.input.absolute, path.join(state.output.absolute, `in${state.input.ext}`), cb),
	(state, p) => p.util.wine.run({cmd : "DirMaster/DirMaster.exe", args : ["--exportall", `in${state.input.ext}`], cwd : state.output.absolute})
];
