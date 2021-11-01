"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "PAK/ARC Compressed Archive",
	website : "http://fileformats.archiveteam.org/wiki/ARC_(compression_format)",
	ext     : [".arc", ".pak"],
	magic   : ["PAK/ARC Compressed archive", "ARC archive data"]
};

exports.converterPriority = ["unar", "arc", "xarc", "UniExtract"];
