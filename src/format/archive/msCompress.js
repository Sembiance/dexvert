/*
import {Format} from "../../Format.js";

export class msCompress extends Format
{
	name = "MS Compress Archive";
	website = "http://fileformats.archiveteam.org/wiki/MS-DOS_installation_compression";
	ext = ["_",".exe"];
	safeExt = undefined;
	magic = ["MS Compress archive data","Microsoft SZDD compressed","Microsoft KWAJ compressed","MS DOS Compression Format"];
	converters = undefined
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MS Compress Archive",
	website : "http://fileformats.archiveteam.org/wiki/MS-DOS_installation_compression",
	ext     : ["_", ".exe"],
	safeExt : () => "_",	// Even self extracting archives need to end in an underscore in order to decompress
	magic   : ["MS Compress archive data", "Microsoft SZDD compressed", "Microsoft KWAJ compressed", "MS DOS Compression Format"]
};

exports.converterPriority = state => (["msexpand", "msexpand_win2k", {program : "deark", flags : {dearkReplaceExt : {".bin" : state.input.ext.trimChars("_")}}}, "UniExtract"]);

*/
