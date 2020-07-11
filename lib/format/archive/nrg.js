"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name    : "Nero CD Image",
	website : "http://fileformats.archiveteam.org/wiki/NRG",
	ext     : [".nrg"],
	magic   : ["Nero CD image"],
	priority : C.PRIORITY.TOP	// NRG is often mis-identified as ISO
};

exports.steps = (state, p) => ([p.util.program.run(p.program.nrg2iso), p.util.program.run(p.program.uniso, {args : [state.input.filePath + ".iso", state.output.dirPath]})]);

