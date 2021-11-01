"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "AMOS Sprite Bank",
	website  : "http://fileformats.archiveteam.org/wiki/AMOS_Sprite_Bank",
	ext      : [".abk"],
	mimeType : "image/x-amos-spritebank",
	magic    : ["AMOS Basic sprite bank", "AMOS Sprites Bank"]
};

exports.converterPriority = ["dumpamos"];
