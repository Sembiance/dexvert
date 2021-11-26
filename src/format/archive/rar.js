/*
import {Format} from "../../Format.js";

export class rar extends Format
{
	name = "Roshal Archive";
	website = "http://fileformats.archiveteam.org/wiki/RAR";
	ext = [".rar"];
	magic = ["RAR archive data","RAR compressed archive","RAR Archive"];
	converters = ["unrar","UniExtract"]

	metaProviders = [""];

post = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Roshal Archive",
	website : "http://fileformats.archiveteam.org/wiki/RAR",
	ext     : [".rar"],
	magic   : ["RAR archive data", "RAR compressed archive", "RAR Archive"]
};

exports.converterPriority = ["unrar", "UniExtract"];

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "unrarMeta"}),
	(state, p) =>
	{
		if(p.util.program.getMeta(state, "unrarMeta"))
			state.input.meta.rar = p.util.program.getMeta(state, "unrarMeta");

		return p.util.flow.noop;
	}
])(state0, p0, cb);

exports.post = (state, p, cb) =>
{
	if(p.util.program.getMeta(state, "unrar"))
	{
		if(!state.input.meta.rar)
			state.input.meta.rar = {};
		
		Object.assign(state.input.meta.rar, p.util.program.getMeta(state, "unrar"));
	}

	if(state.input.meta.rar.passwordProtected)
		state.processed = true;
		
	setImmediate(cb);
};


*/
