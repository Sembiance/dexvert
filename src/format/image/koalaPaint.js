/*
import {Format} from "../../Format.js";

export class koalaPaint extends Format
{
	name = "Koala Paint";
	website = "http://fileformats.archiveteam.org/wiki/KoalaPainter";
	ext = [".koa",".gig",".kla",".gg",".koala"];
	safeExt = undefined;
	mimeType = "image/x-koa";
	magic = ["Koala Paint"];
	trustMagic = true;
	converters = ["nconvert",`abydosconvert[format:${this.mimeType}]`,"view64"]

idCheck = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Koala Paint",
	website  : "http://fileformats.archiveteam.org/wiki/KoalaPainter",
	ext      : [".koa", ".gig", ".kla", ".gg", ".koala"],
	safeExt  : state =>
	{
		if([10003, 10006].includes(fs.statSync(state.input.absolute).size))
			return ".koa";

		// nconvert requires a proper file extension. If the file is not 10,003 or 10,006 bytes, we assume it is compressed and needs a .gg extension to convert correctly
		return ".gg";
	},
	mimeType   : "image/x-koa",
	magic      : ["Koala Paint"],
	trustMagic : true // Koala Paint is normally untrustworthy, but we trust it here
};

// Must be greater <= 10006 because either we are uncompressed (10003/10006) or we are compresed in which case we should be smaller
exports.idCheck = state => fs.statSync(state.input.absolute).size<=10006;

exports.converterPriority = ["nconvert", `abydosconvert[format:${this.mimeType}]`, "view64"];

*/
