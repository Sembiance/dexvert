"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "ZX Spectrum BSP",
	website        : "http://fileformats.archiveteam.org/wiki/BSP_(ZX_Spectrum)",
	ext            : [".bsp"],
	forbidExtMatch : true,
	magic          : ["ZX Spectrum BSP", "BSP bitmap"]
};

exports.converterPriority = ["recoil2png"];
