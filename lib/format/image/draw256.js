"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name        : "Draw 256 Image",
	website     : "http://fileformats.archiveteam.org/wiki/Draw256",
	ext         : [".vga"],
	unsafe : true,
	priority    : C.PRIORITY.VERYLOW,
	notes       : "Draw256 from DOS correctly loads these formats, but sadly will take invalid .VGA files and render a garbage/static. Couldn't find any more info about the file format to try and determine ahead of time that it's a proper VGA file."
};

exports.steps =
[
	(state, p) => p.util.dos.run({state, p,
		subdir   : "DRAW256",
		autoExec : ["CD DRAW256", `DRAW256.EXE ..\\${state.input.filePath}`],
		timeout  : XU.MINUTE,
		keys     : ["s", "..\\F.PCX", ["Return"], ["Escape"], "y"]}),
	() => ({program : "convert", argsd : ["F.PCX"]})
];
