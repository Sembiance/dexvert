"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Degas Elite Brush",
	website             : "http://fileformats.archiveteam.org/wiki/DEGAS_Elite_brush",
	ext                 : [".bru"],
	fileSize            : 64,
	forbidFileSizeMatch : true

};

exports.converterPriorty = ["recoil2png"];
