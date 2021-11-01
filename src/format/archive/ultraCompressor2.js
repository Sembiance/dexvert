"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "UltraCompressor II Archive",
	website : "http://fileformats.archiveteam.org/wiki/UC2",
	ext     : [".uc2"],
	magic   : ["UC2 archive data", "UltraCompressor 2 Archive"]
};

exports.converterPriority = ["ultraCompressor2"];
