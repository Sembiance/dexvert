"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Tape Archive",
	website : "http://fileformats.archiveteam.org/wiki/Tar",
	ext     : [".tar", ".gtar"],
	magic   : ["TAR - Tape ARchive", /.* tar archive/, /^tar archive$/]
};

exports.converterPriority = ["tar", "7z", "UniExtract"];
