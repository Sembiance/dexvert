"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name     : "3D Construction Kit",
	ext      : [".run"],
	magic    : ["3D Construction Kit game Runner"]
};

exports.steps =
[
	(state, p) => p.util.dos.run({p,
		bin : "RUNVGA.EXE",
		autoExec : [`RUNVGA.EXE ${state.input.filePath}`],
		timeout : XU.SECOND*15,
		screenshot : {filePath : path.join(state.output.absolute, `${state.input.name}.png`), loc : -(XU.SECOND*3)},
		keyOpts : {delay : XU.SECOND*10},
		keys : ["1"]})
];
