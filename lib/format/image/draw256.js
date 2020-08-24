"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Draw 256 Image",
	website  : "http://fileformats.archiveteam.org/wiki/Draw256",
	ext      : [".vga"]
};

exports.steps =
[
	(state, p) => p.util.dos.run({p,
		subdir   : "DRAW256",
		autoExec : ["CD DRAW256", `DRAW256.EXE ..\\${state.input.filePath}`],
		timeout  : XU.MINUTE,
		keys     : ["s", "..\\F.PCX", ["Return"], ["Escape"], "y"]}),
	(state, p) => ({program : "convert", args : p.program.convert.args(state, p, "F.PCX")})
];
