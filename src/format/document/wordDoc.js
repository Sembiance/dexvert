/*
import {Format} from "../../Format.js";

export class wordDoc extends Format
{
	name = "Word Document";
	website = "http://fileformats.archiveteam.org/wiki/DOC";
	ext = [".doc"];
	forbidExtMatch = true;
	magic = ["Microsoft Word document","Microsoft Word for Windows"];
	unsafe = true;
	converters = ["fileMerlin","antiword","soffice"]

post = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Word Document",
	website        : "http://fileformats.archiveteam.org/wiki/DOC",
	ext            : [".doc"],
	forbidExtMatch : true,
	magic          : ["Microsoft Word document", "Microsoft Word for Windows"],
	unsafe         : true
};

exports.converterPriority = ["fileMerlin", "antiword", "soffice"];

exports.post = (state, p, cb) =>
{
	if((p.util.program.getMeta(state, "antiword") || {}).passwordProtected)
	{
		state.input.meta.wordDoc = {passwordProtected : true};
		state.processed = true;
	}
		
	setImmediate(cb);
};


*/
