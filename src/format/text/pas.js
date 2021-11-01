/*
import {Format} from "../../Format.js";

export class pas extends Format
{
	name = "Pascal/Delphi Source File";
	website = "http://fileformats.archiveteam.org/wiki/Pascal";
	ext = [".pas",".tp5"];
	forbidExtMatch = true;
	magic = ["ASCII text","ISO-8859 text","UTF-8 Unicode text","Non-ISO extended-ASCII text","ReStructuredText file","International EBCDIC text","UTF-8 Unicode text","Printable ASCII","Unicode text, UTF-8 text","Algol 68 source, ISO-8859 text","Delphi Project source"];
	weakMagic = true;
	untouched = true;
	hljsLang = "delphi";

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Pascal/Delphi Source File",
	website        : "http://fileformats.archiveteam.org/wiki/Pascal",
	ext            : [".pas", ".tp5"],
	forbidExtMatch : true,
	magic          : [...C.TEXT_MAGIC, "Delphi Project source"],
	weakMagic      : true,
	untouched      : true,
	hljsLang       : "delphi"
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
