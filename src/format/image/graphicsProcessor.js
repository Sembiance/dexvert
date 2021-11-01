"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Graphics Processor",
	website  : "http://fileformats.archiveteam.org/wiki/Graphics_Processor",
	ext      : [".pg1", ".pg2", ".pg3"],
	fileSize : 32331
};

exports.converterPriority = ["recoil2png"];
