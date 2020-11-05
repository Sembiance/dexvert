"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "STAD PAC",
	website  : "http://fileformats.archiveteam.org/wiki/STAD_PAC",
	ext      : [".pac", ".seq"],
	mimeType : "image/x-stad",
	magic    : ["STAD hi-res", "Atari ST STAD bitmap image data"]
};

exports.converterPriorty = ["abydosconvert", "nconvert", "recoil2png"];
