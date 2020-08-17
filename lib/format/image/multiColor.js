"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "ZX Spectrum Multicolor",
	website  : "http://fileformats.archiveteam.org/wiki/Multicolor_(ZX_Spectrum)",
	ext      : [".ifl", ".mc", ".mlt"],
	filesize : [9216, 12288, 12288]
};

exports.converterPriorty = ["recoil2png"];
