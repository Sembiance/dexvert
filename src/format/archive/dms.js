"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Amiga Disk Master System Archive",
	website : "http://fileformats.archiveteam.org/wiki/Disk_Masher_System",
	ext      : [".dms", ".fms"],
	magic    : ["Disk Masher System compressed disk image", "DMS archive data"]
};

exports.converterPriority = ["unar"];
