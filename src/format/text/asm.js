/*
import {Format} from "../../Format.js";

export class asm extends Format
{
	name = "Assembly Source File";
	website = "http://fileformats.archiveteam.org/wiki/Assembly_language";
	ext = [".asm"];
	forbidExtMatch = true;
	magic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text","C source"];
	weakMagic = true;
	untouched = true;
	hljsLang = "x86asm";

metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Assembly Source File",
	website        : "http://fileformats.archiveteam.org/wiki/Assembly_language",
	ext            : [".asm"],
	forbidExtMatch : true,
	magic          : [...C.TEXT_MAGIC, "C source"], // file often confuses assembly for C source and nothing else identifies it
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "x86asm"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
