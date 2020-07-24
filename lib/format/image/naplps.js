"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name           : "NAPLPS Image",
	website        : "http://fileformats.archiveteam.org/wiki/NAPLPS",
	ext            : [".nap"],
	forbidExtMatch : true,
	magic          : ["NAPLPS graphics", "NAPLPS Image"],
	unsupportedNotes : `Some NAP files are actually animations. TURSHOW does actually show these, but sadly I can't detect this. So for now I treat all NAP files as just single images.`
};

exports.steps =
[
	(state, p) => p.util.dos.run({p,
		subdir     : "TURSHOW/TURSHOW.EXE",
		autoExec   : [`TURSHOW.EXE ${state.input.filePath}`],
		screenshot : {filePath : path.join(state.output.absolute, `${state.input.name}.png`), loc : -(XU.SECOND*12)},
		timeout    : XU.MINUTE}),
	state => ({program : "convert", args : ["OUT.TGA", "-flip", "-strip", path.join(state.output.dirPath, "outfile.png")]})
];
