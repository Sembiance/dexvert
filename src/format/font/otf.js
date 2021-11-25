/*
import {Format} from "../../Format.js";

export class otf extends Format
{
	name = "OpenType Font";
	website = "http://fileformats.archiveteam.org/wiki/OpenType";
	ext = [".otf"];
	magic = [{}];
	untouched = true;

steps = [null];

metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "OpenType Font",
	website   : "http://fileformats.archiveteam.org/wiki/OpenType",
	ext       : [".otf"],
	magic     : [/^OpenType [Ff]ont/],
	untouched : true
};

exports.steps = [(state, p) => p.util.flow.serial(p.family.previewSteps)];

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	(state, p) => p.family.supportedInputMeta,
	() => ({program : "otfinfo"}),
	(state, p) =>
	{
		if(p.util.program.getMeta(state, "otfinfo"))
			state.input.meta.otf = p.util.program.getMeta(state, "otfinfo");
		
		return p.util.flow.noop;
	}
])(state0, p0, cb);

*/
