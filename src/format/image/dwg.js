"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "AutoCAD Drawing",
	website : "http://fileformats.archiveteam.org/wiki/DWG",
	ext     : [".dwg", ".dwt"],
	magic   : [/^AutoCAD R.+ Drawing/, "DWG AutoDesk AutoCAD"]
};

exports.converterPriority = ["totalCADConverterX", "dwg2SVG", "dwg2bmp", "uniconvertor", "irfanView", "nconvert"];
