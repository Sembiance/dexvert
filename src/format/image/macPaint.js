"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "MacPaint Image",
	website        : "http://fileformats.archiveteam.org/wiki/MacPaint",
	ext            : [".mac", ".pntg", ".pic"],
	magic          : ["MacPaint image data"],
	mimeType       : "image/x-macpaint",
	forbiddenMagic : ["Installer VISE Mac package"]
};

// deark correctly identifies the original filename from meta info within the file itself
exports.converterPriority = ["deark", "abydosconvert"];
