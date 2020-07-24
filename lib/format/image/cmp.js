"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name     : "LEADTools Compressed Image",
	website  : "http://fileformats.archiveteam.org/wiki/CMP",
	ext      : [".cmp"],
	magic    : ["LEADTools CMP Image Compressed bitmap", "LEADToolsCompressed Image"]
};

exports.steps =
[
	(state, p) => p.util.dos.run({p,
		bin : "LEADTOOL/LEADECOM.EXE",
		autoExec : [`LEADECOM.EXE ${state.input.filePath} OUT.TGA /TGA24`],
		timeout : XU.MINUTE}),
	state => ({program : "convert", args : ["OUT.TGA", "-flip", "-strip", path.join(state.output.dirPath, "outfile.png")]})
];
