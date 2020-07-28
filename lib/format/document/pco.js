"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name        : "PC-Outline Document",
	website     : "http://fileformats.archiveteam.org/wiki/PC-Outline",
	ext         : [".pco"],
	magic       : ["PC-Outline outline"]
};

exports.steps =
[
	(state, p) => p.util.dos.run({p,
		subdir   : "PCO",
		autoExec : [`COPY ${state.input.filePath.toUpperCase()} PCO\\F.PCO`, "CD PCO", "PCO.EXE"],
		timeout  : XU.MINUTE*2,
		keys     : [" ", " ", ["Down"], ["Return"], ["Return"], {delay : XU.SECOND*5}, ["Insert"], ["Right"], ["Right"], ["Right"], ["Right"], "d", "a", "g", "E:\\OUTFILE.TXT", ["Return"], ["Escape"], ["Escape"], "y"]}),
	(state, p) => p.util.file.move(path.join(state.cwd, "OUTFILE.TXT"), path.join(state.output.absolute, `${state.input.name}.txt`))
];
