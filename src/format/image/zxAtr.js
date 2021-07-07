"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "ZX Spectrum Attributes Image",
	website             : "http://fileformats.archiveteam.org/wiki/ATR_(ZX_Spectrum)",
	ext                 : [".atr"],
	fileSize            : 768,
	forbidFileSizeMatch : true
};

exports.converterPriorty = ["recoil2png"];
