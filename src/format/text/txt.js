/*
import {Format} from "../../Format.js";

export class txt extends Format
{
	name = "Text File";
	website = "http://fileformats.archiveteam.org/wiki/Text";
	magic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text"];
	priority = 5;
	fallback = true;
	untouched = true;

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

// Fallback match for anything that is just text. This will only be matched as a last resort
exports.meta =
{
	name      : "Text File",
	website   : "http://fileformats.archiveteam.org/wiki/Text",
	magic     : C.TEXT_MAGIC,
	priority  : C.PRIORITY.LOWEST,
	fallback  : true,
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
