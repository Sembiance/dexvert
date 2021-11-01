"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "ZX Spectrum ULA+",
	website             : "https://zxart.ee/eng/graphics/database/pictureType:ulaplus/sortParameter:date/sortOrder:desc/resultsType:zxitem/",
	ext                 : [".scr"],
	fileSize            : 6976,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
