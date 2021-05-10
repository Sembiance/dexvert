"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Truevision Targa Graphic",
	website  : "http://fileformats.archiveteam.org/wiki/TGA",
	ext      : [".tga", ".targa", ".tpic", ".icb", ".vda", ".vst"],
	mimeType : "image/x-tga",
	magic    : ["Truevision TGA", "Targa image data"]
};

// ImageMagick sometimes doesn't detect that a TGA image has been rotated. These other converters seem to do a better job at that
// Only deark was able to correctly handle flag_b32.tga
exports.converterPriorty = ["deark", "nconvert", "recoil2png", "abydosconvert"];
