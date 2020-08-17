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
	magic          : ["iCEDraw graphic"],
	forbiddenMagic : C.TEXT_MAGIC,
	bruteUnsafe    : true
};

exports.converterPriorty = ["ansilove", "abydosconvert"];
