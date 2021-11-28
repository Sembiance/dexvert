/*
import {Format} from "../../Format.js";

export class rexx extends Format
{
	name = "OS/2 REXX Batch file";
	website = "https://www.tutorialspoint.com/rexx/index.htm";
	ext = [".cmd",".rexx",".rex"];
	forbidExtMatch = true;
	magic = ["OS/2 REXX batch file","ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text"];
	weakMagic = true;
	untouched = true;

	metaProvider = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "OS/2 REXX Batch file",
	website        : "https://www.tutorialspoint.com/rexx/index.htm",
	ext            : [".cmd", ".rexx", ".rex"],
	forbidExtMatch : true,
	magic          : ["OS/2 REXX batch file", ...C.TEXT_MAGIC],
	weakMagic      : true,
	untouched      : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
