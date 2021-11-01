"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "PC-Board",
	website        : "http://fileformats.archiveteam.org/wiki/PCBoard",
	forbidExtMatch : true,
	ext            : [".pcb"],
	mimeType       : "text/x-pcboard",
	magic          : [/^data$/, "ISO-8859 text"],
	weakMagic      : true,
	unsafe         : true
};

// We do NOT use abydos, because it just falls back to ansilove
exports.converterPriority = ["ansilove"];
