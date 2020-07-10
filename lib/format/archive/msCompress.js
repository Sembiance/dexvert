"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "MS Compress Archive",
	website : "http://fileformats.archiveteam.org/wiki/MS-DOS_installation_compression",
	ext     : ["_"],
	magic   : ["MS Compress archive data", "Microsoft SZDD compressed", "MS DOS Compression Format"],
	program : "msexpand"
};
