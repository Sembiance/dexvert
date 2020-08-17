"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "PC-Board",
	website        : "http://fileformats.archiveteam.org/wiki/PCBoard",
	ext            : [".pcb"],
	mimeType       : "text/x-pcboard",
	magic          : [/^data$/, "ISO-8859 text"],
	weakMagic      : true,
	bruteUnsafe    : true
};

exports.converterPriorty = ["ansilove", "abydosconvert"];
