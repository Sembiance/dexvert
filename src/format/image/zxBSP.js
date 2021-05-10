"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "ZX Spectrum BSP",
	website     : "http://fileformats.archiveteam.org/wiki/BSP_(ZX_Spectrum)",
	ext         : [".bsp"],
	magic       : ["ZX Spectrum BSP", "BSP bitmap"]
};

exports.converterPriorty = ["recoil2png"];
