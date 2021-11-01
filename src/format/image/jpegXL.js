"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "JPEG XL",
	website     : "http://fileformats.archiveteam.org/wiki/JPEG_XL",
	ext         : [".jxl"],
	mimeType    : "image/jxl",
	magic       : ["JPEG XL codestream", "JPEG XL bitmap"],
	weakMagic   : true,
	unsupported : true,
	notes       : "Modern format. Pain in the butt to build the JPEG-XL reference package, I started, see overlay/legacy/JPEG-XL but then gave up because meh."
};

//exports.converterPriority = ["djxl", "abydosconvert"];
