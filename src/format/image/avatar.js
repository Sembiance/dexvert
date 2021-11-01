"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Avatar/0",
	website        : "http://fileformats.archiveteam.org/wiki/AVATAR",
	ext            : [".avt"],
	mimeType       : "text/x-avatar0",
	forbiddenMagic : C.TEXT_MAGIC,
	unsafe         : true
};

exports.converterPriority = ["abydosconvert"];
