"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Segmented Hypergraphics Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/Segmented_Hypergraphics",
	ext      : [".shg"],
	magic    : ["Segmented Hypergraphics bitmap"]
};

exports.converterPriority = ["deark"];
