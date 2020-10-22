"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "True Paint I",
	website  : "http://fileformats.archiveteam.org/wiki/True_Paint_I",
	ext      : [".mci", ".mcp"],
	fileSize : {".mci" : 19434}
};

exports.converterPriorty = ["recoil2png"];
