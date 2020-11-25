"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "Digi-Pic DGI",
	website : "http://fileformats.archiveteam.org/wiki/DGI_(Digi-Pic)",
	ext     : [".dgi"],
	notes   : "Currently only support converting in black in white. Looks like there may be more color information available?"
};

exports.steps =
[
	(state, p) => p.util.dos.run({state, p,
		bin : "CONV125/DGIWIND.EXE",
		autoExec : [`DGIWIND.EXE ${state.input.filePath}`],
		timeout : XU.MINUTE}),
	state => ({program : "recoil2png", args : [path.join(state.cwd, "IN.MSP")]}),
	(state, p) => p.util.file.move(path.join(state.cwd, "IN.png"), path.join(state.output.absolute, `${state.input.name}.png`))
];
