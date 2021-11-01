"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Device Independent File",
	website        : "http://fileformats.archiveteam.org/wiki/DVI_(Device_Independent_File_Format)",
	ext            : [".dvi"],
	forbidExtMatch : true,
	magic          : ["TeX DVI file", "Device Independent Document"]
};

exports.converterPriority = ["dvi2pdf"];

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "dviinfox"}),
	(state, p) =>
	{
		if(p.util.program.getMeta(state, "dviinfox"))
			state.input.meta.deviceIndependentFile = p.util.program.getMeta(state, "dviinfox");
		
		return p.util.flow.noop;
	}
])(state0, p0, cb);
