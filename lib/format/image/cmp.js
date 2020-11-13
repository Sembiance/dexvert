"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "LEADTools Compressed Image",
	website  : "http://fileformats.archiveteam.org/wiki/CMP",
	ext      : [".cmp"],
	magic    : ["LEADTools CMP Image Compressed bitmap", "LEADToolsCompressed Image"]
};

exports.steps =
[
	(state, p) => p.util.dos.run({state, p,
		bin : "LEADTOOL/LEADECOM.EXE",
		autoExec : [`LEADECOM.EXE ${state.input.filePath} OUT.TGA /TGA24`],
		timeout : XU.MINUTE}),
	(state, p) => ({program : "convert", args : ["OUT.TGA", "-flip", ...p.util.program.args(state, p, "convert").slice(1)]})
];
