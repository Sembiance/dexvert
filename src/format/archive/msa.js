"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Magic Shadow Archiver",
	website : "http://fileformats.archiveteam.org/wiki/MSA_(Atari)",
	ext     : [".msa"],
	magic   : ["Atari MSA archive data", "Atari MSA Disk Image"],
	notes   : "Unable to extract anything from adr_1.msa. The msa.exe program also fails to find any data. Yet a hex editor shows data. No other converters known."
};

exports.converterPriority = ["deark"];
