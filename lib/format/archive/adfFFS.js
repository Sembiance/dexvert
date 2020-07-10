"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Amiga Disk Format (FFS)",
	website : "http://fileformats.archiveteam.org/wiki/ADF_(Amiga)",
	ext     : [".adf"],
	magic   : ["Amiga Disk image File (FFS)", "Amiga FFS disk", "Amiga Inter FFS disk", "Amiga Fastdir FFS disk"],
	program : "xdftool"
};
