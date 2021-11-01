"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Amiga Disk Format (FFS)",
	website  : "http://fileformats.archiveteam.org/wiki/ADF_(Amiga)",
	ext      : [".adf"],
	fileSize : 901120,
	magic    : ["Amiga Disk image File (FFS)", "Amiga FFS disk", "Amiga Inter FFS disk", "Amiga Fastdir FFS disk"]
};

exports.converterPriority = ["unadf", "xdftool"];
