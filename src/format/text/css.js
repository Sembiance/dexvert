/*
import {Format} from "../../Format.js";

export class css extends Format
{
	name = "Cascading Style Sheet File";
	website = "http://fileformats.archiveteam.org/wiki/CSS";
	ext = [".css"];
	mimeType = "text/css";
	forbidExtMatch = true;
	magic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text","assembler source"];
	weakMagic = true;
	untouched = true;
	hljsLang = "css";

	metaProvider = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Cascading Style Sheet File",
	website        : "http://fileformats.archiveteam.org/wiki/CSS",
	ext            : [".css"],
	mimeType       : "text/css",
	forbidExtMatch : true,
	magic          : [...C.TEXT_MAGIC, "assembler source"],	// Sadly file often detects it as assembler source and no other indentifiers come back with magic
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "css"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
