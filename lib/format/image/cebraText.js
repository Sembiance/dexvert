"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name        : "CebraText",
	website     : "http://fileformats.archiveteam.org/wiki/CebraText",
	ext         : [".ttx"],
	magic       : ["Cebra Teletext page"],
	unsupported : true,
	notes       : "CebraText came out in 2003 for Windows. Sadly, it doesn't work with wine and I couldn't find any converter programs that supported the file format."
};
