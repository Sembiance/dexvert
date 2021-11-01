"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Spectrum 512 Extended",
	website : "http://fileformats.archiveteam.org/wiki/Spectrum_512_formats",
	ext     : [".spx"],
	magic   : ["Spectrum 512 Extended bitmap"]
};

exports.converterPriority = ["recoil2png"];
