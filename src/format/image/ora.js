"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "OpenRaster",
	website  : "http://fileformats.archiveteam.org/wiki/OpenRaster",
	ext      : [".ora"],
	mimeType : "image/openraster",
	magic    : ["OpenRaster Image Format", "OpenRaster bitmap"]
};

exports.converterPriority = ["deark"];
