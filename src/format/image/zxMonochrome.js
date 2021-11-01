"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "ZX Monochrome",
	website             : "https://zxart.ee/eng/graphics/database/pictureType:monochrome/sortParameter:date/sortOrder:desc/resultsType:zxitem/",
	ext                 : [".scr"],
	fileSize            : 6144,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
