"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "ZX Spectrum Border Screen",
	website     : "http://fileformats.archiveteam.org/wiki/BSP_(ZX_Spectrum)",
	ext         : [".bsp"],
	magic       : ["ZX Spectrum BSP"],
	unsupported : true,
	notes       : "No known converters."
};

exports.converterPriorty = ["recoil2png"];
