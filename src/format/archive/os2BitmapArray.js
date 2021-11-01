"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "OS/2 Bitmap Array",
	website : "http://fileformats.archiveteam.org/wiki/OS/2_Bitmap_Array",
	magic   : ["OS/2 graphic array", "OS/2 Bitmap Graphics Array"],
	ext     : [".bga", ".bmp", ".ico"]
};

exports.converterPriority = ["deark"];
