"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name        : "Draw 256 Image",
	website     : "http://fileformats.archiveteam.org/wiki/Draw256",
	ext         : [".vga"],
	unsafe      : true,
	priority    : C.PRIORITY.VERYLOW,
	mimeType    : "image/x-draw256-vga",
	unsupported : true,
	notes       : ".vga is a very common extension and there is no known magic and draw256 converts any .vga file as garbage and abydos also converts non real .vga files into static. So this format is not supported (also haven't encountered any of these images)"
};

//exports.converterPriority = ["abydosconvert", "draw256"];
