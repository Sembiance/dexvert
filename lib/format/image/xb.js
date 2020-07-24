"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Extended Binary",
	website        : "http://fileformats.archiveteam.org/wiki/XBIN",
	ext            : [".xb"],
	forbidExtMatch : true,
	mimeType       : "image/x-xbin",
	magic          : ["XBIN image"],
	bruteUnsafe    : true
};

exports.converterPriorty = ["ansilove", "abydosconvert"];
