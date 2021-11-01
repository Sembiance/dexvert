"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Spectrum 512 Compressed",
	website  : "http://fileformats.archiveteam.org/wiki/Spectrum_512_formats",
	ext      : [".spc"],
	mimeType : "image/x-spectrum512-compressed",
	magic    : ["Spectrum 512 compressed"]
};

exports.converterPriority = ["recoil2png"];
