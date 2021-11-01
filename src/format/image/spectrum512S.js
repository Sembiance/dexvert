"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Spectrum 512 Smooshed",
	website  : "http://fileformats.archiveteam.org/wiki/Spectrum_512_formats",
	ext      : [".sps"],
	mimeType : "image/x-spectrum512-smooshed",
	magic    : ["Spectrum 512 compressed/smooshed bitmap"],
	notes    : "Some test files fail to convert correctly: AMBER_F, CANDLE, AI_R_010"
};

exports.converterPriority = ["recoil2png", "abydosconvert", "nconvert", "deark"];
