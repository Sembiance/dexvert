"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name           : "PC-Board",
	website        : "http://fileformats.archiveteam.org/wiki/PCBoard",
	ext            : [".pcb"],
	mimeType       : "text/x-pcboard",
	magic          : [/^data$/],
	forbiddenMagic : C.TEXT_MAGIC,
	weakMagic      : true,
	bruteUnsafe    : true
};

exports.converterPriorty = ["ansilove", "abydosconvert"];
