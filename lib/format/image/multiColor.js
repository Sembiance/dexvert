"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "ZX Spectrum Multicolor",
	website  : "http://fileformats.archiveteam.org/wiki/Multicolor_(ZX_Spectrum)",
	ext      : [".ifl", ".mc", ".mlt"],
	filesize : [state => ({".ifl" : 9216, ".mc" : 12288, ".mlt" : 12288}[state.input.ext.toLowerCase()])]
};

exports.converterPriorty = ["recoil2png"];
