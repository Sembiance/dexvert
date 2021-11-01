"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Genus Graphics Library Compressed Archive",
	website : "http://fileformats.archiveteam.org/wiki/Genus_Graphics_Library",
	ext     : [".gx", ".gxl"],
	magic   : ["Genus Graphics Library"]
};

exports.converterPriority = ["unpcxgx"];
