"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name           : "iCEDraw Format",
	website        : "http://fileformats.archiveteam.org/wiki/ICEDraw",
	ext            : [".idf"],
	mimeType       : "image/x-icedraw",
	magic          : [/^data$/],
	forbiddenMagic : C.TEXT_MAGIC,
	weakMagic      : true,
	bruteUnsafe    : true
};

exports.converterPriorty = ["ansilove", "abydosconvert"];
