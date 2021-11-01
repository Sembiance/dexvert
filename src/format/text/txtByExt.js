/*
import {Format} from "../../Format.js";

export class txtByExt extends Format
{
	name = "Text File";
	website = "http://fileformats.archiveteam.org/wiki/Text";
	magic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text"];
	forbiddenMagic = ["TROFF markup"];
	weakMagic = true;
	priority = 4;
	ext = [".txt",".rea",".doc",".docs",".english",".credits",".info",".inf",".log",".ascii",".nfo",".cfg",".config",".frm",".hlp",".advert",".advert2"];
	forbidExtMatch = true;
	untouched = true;
	fallback = true;

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

// txtByExt handles files with specific extensions that are likely text but have non-ascii characters which requires loosened magic match of /^data$/
exports.meta =
{
	name           : "Text File",
	website        : "http://fileformats.archiveteam.org/wiki/Text",
	magic          : Array.from(C.TEXT_MAGIC),
	forbiddenMagic : ["TROFF markup"],
	weakMagic      : true,
	priority       : C.PRIORITY.VERYLOW,
	ext            :
	[
		".txt", ".rea", ".doc", ".docs", ".english", ".credits", ".info", ".inf", ".log", ".ascii", ".nfo",
		".cfg", ".config",
		".frm", ".hlp",
		".advert", ".advert2"
	],
	forbidExtMatch : true,
	untouched      : true,
	fallback       : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
