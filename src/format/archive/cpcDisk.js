"use strict";
const XU = require("@sembiance/xu");
	
exports.meta =
{
	name    : "Amstrad CPC Disk",
	website : "http://fileformats.archiveteam.org/wiki/DSK_(CPCEMU)",
	ext     : [".dsk"],
	magic   : ["Extended CPCEMU style disk image", "Amstrad/Spectrum Extended .DSK data"]
};

exports.converterPriorty = ["cpcxfs"];
