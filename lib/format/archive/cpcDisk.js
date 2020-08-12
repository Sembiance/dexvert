"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "Amstrad CPC Disk",
	website : "http://fileformats.archiveteam.org/wiki/DSK_(CPCEMU)",
	ext     : [".dsk"],
	magic   : ["Extended CPCEMU style disk image", "Amstrad/Spectrum Extended .DSK data"]
};

exports.steps = [(state, p) => p.util.wine.run({cmd : "cpcxfs/cpcxfsw.exe", args : [path.join(state.cwd, state.input.filePath), "-mg", "*.*"], cwd : state.output.absolute})];
