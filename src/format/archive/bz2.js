"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "BZip2 archive",
	website : "http://fileformats.archiveteam.org/wiki/BZ2",
	ext     : [".bz2", ".bzip2"],
	magic   : ["bzip2 compressed data", "bzip2 compressed archive", "BZIP2 Compressed Archive"]
};

exports.converterPriority = ["bunzip2", {program : "7z", flags : {"7zSingleFile" : true}}, "UniExtract"];
