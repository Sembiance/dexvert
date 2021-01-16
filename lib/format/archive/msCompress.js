"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MS Compress Archive",
	website : "http://fileformats.archiveteam.org/wiki/MS-DOS_installation_compression",
	ext     : ["_", ".exe"],
	safeExt : () => "_",	// Even self extracting archives need to end in an underscore in order to decompress
	magic   : ["MS Compress archive data", "Microsoft SZDD compressed", "MS DOS Compression Format"]
};

exports.converterPriorty = ["msexpand"];
