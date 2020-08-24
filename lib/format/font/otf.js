"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "OpenType Font",
	website : "http://fileformats.archiveteam.org/wiki/OpenType",
	ext     : [".otf"],
	magic   : [/^OpenType [Ff]ont/]
};

exports.steps = [(state, p) => p.util.flow.serial(p.family.previewSteps)];

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	(state, p) => p.family.supportedInputMeta,
	() => ({program : "otfinfo"}),
	(state, p) =>
	{
		if(state.run.meta.otfinfo)
		{
			state.input.meta.otf = state.run.meta.otfinfo;
			delete state.run.meta.otfinfo;
		}
		
		return p.util.flow.noop;
	}
])(state0, p0, cb);
