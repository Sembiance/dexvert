"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "ZX Spectrum Multicolor",
	website  : "http://fileformats.archiveteam.org/wiki/Multicolor_(ZX_Spectrum)",
	ext      : [".ifl", ".mc", ".mlt"],
	fileSize : {".ifl" : 9216, ".mc,.mlt" : 12288}
};

exports.converterPriority = ["recoil2png"];
