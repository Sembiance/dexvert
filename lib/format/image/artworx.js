"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name           : "ArtWorx Data Format",
	website        : "http://fileformats.archiveteam.org/wiki/ArtWorx_Data_Format",
	ext            : [".adf"],
	mimeType       : "image/x-artworx",
	magic          : [/^data$/],
	forbiddenMagic : ["Amiga Disk image File", ...C.TEXT_MAGIC],
	weakMagic      : true,
	bruteUnsafe    : true
};

exports.converterPriorty = ["ansilove", "abydosconvert"];
