"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "Tagged Image File Format",
	website          : "http://fileformats.archiveteam.org/wiki/TIFF",
	ext              : [".tif", ".tiff"],
	mimeType         : "image/tiff",
	magic            : ["Tagged Image File Format", "TIFF image data"]
};

exports.converterPriorty = ["convert"];
