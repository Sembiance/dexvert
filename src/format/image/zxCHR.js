"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "ZX Spectrum CHR$",
	website : "http://fileformats.archiveteam.org/wiki/CH$",
	ext     : [".ch$"],
	magic   : ["ZX Spectrum CHR$ bitmap", "ZX Spectrum CHR"]
};

exports.converterPriority = ["recoil2png"];
