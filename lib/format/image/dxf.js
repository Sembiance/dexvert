"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Drawing Exchange Format",
	website  : "http://fileformats.archiveteam.org/wiki/DXF",
	ext      : [".dxf"],
	mimeType : "image/vnd.dxf",
	magic : [/^AutoCAD Drawing [Ee][Xx]change Format/, "Drawing Interchange File Format"]
};

exports.converterPriorty = ["dxf-to-svg"];
