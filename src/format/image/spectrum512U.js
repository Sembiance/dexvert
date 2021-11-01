"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Spectrum 512 Uncompressed",
	website  : "http://fileformats.archiveteam.org/wiki/Spectrum_512_formats",
	ext      : [".spu"],
	mimeType : "image/x-spectrum512-uncompressed"
};

exports.converterPriority = ["recoil2png"];
