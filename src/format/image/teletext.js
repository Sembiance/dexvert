/*
import {Format} from "../../Format.js";

export class teletext extends Format
{
	name = "Teletext";
	website = "http://snisurset.net/code/abydos/teletext.html";
	ext = [".bin"];
	forbidExtMatch = true;
	forbiddenMagic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text"];
	unsafe = true;
	mimeType = "text/x-raw-teletext";
	unsupported = true;
	notes = "Can't determine any reliable way to determine if a file is RAW teletext. Abydos will convert any garbage and .bin is far too generic an extension to match on.";
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Teletext",
	website        : "http://snisurset.net/code/abydos/teletext.html",
	ext            : [".bin"],
	forbidExtMatch : true,
	forbiddenMagic : C.TEXT_MAGIC,
	unsafe    : true,
	mimeType       : "text/x-raw-teletext",
	unsupported    : true,
	notes          : "Can't determine any reliable way to determine if a file is RAW teletext. Abydos will convert any garbage and .bin is far too generic an extension to match on."
};

*/
