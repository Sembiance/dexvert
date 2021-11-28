/*
import {Format} from "../../Format.js";

export class batDOS extends Format
{
	name = "DOS Batch File";
	website = "http://fileformats.archiveteam.org/wiki/BAT";
	ext = [".bat"];
	forbidExtMatch = true;
	magic = ["DOS batch file","ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text",{}];
	weakMagic = true;
	untouched = true;
	hljsLang = "bat";

	metaProvider = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "DOS Batch File",
	website        : "http://fileformats.archiveteam.org/wiki/BAT",
	ext            : [".bat"],
	forbidExtMatch : true,
	magic          : ["DOS batch file", ...C.TEXT_MAGIC, /^data$/],
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "bat"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
