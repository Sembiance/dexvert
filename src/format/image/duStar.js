"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Atari DU* Image",
	website  : "http://fileformats.archiveteam.org/wiki/DU*",
	ext      : [".du1", ".du2", ".duo"],
	mimeType : "image/x-atari-duo",
	fileSize : 113600
};

exports.converterPriority = ["recoil2png", "abydosconvert"];
