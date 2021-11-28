/*
import {Format} from "../../Format.js";

export class pdf extends Format
{
	name = "Portable Document Format";
	website = "http://fileformats.archiveteam.org/wiki/PDF";
	ext = [".pdf"];
	mimeType = "application/pdf";
	magic = ["Adobe Portable Document Format","PDF document",{}];
	untouched = true;

	metaProvider = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Portable Document Format",
	website   : "http://fileformats.archiveteam.org/wiki/PDF",
	ext       : [".pdf"],
	mimeType  : "application/pdf",
	magic     : ["Adobe Portable Document Format", "PDF document", /Acrobat PDF.* Portable Document Format$/],
	untouched : true
};

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "pdfinfo"}),
	(state, p) =>
	{
		if(p.util.program.getMeta(state, "pdfinfo"))
		{
			state.input.meta.pdf = p.util.program.getMeta(state, "pdfinfo");
			state.processed = true;
		}
		
		return p.util.flow.noop;
	}
])(state0, p0, cb);

*/
