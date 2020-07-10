"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Amiga Disk Master System Archive",
	ext      : [".dms", ".fms"],
	magic    : ["Disk Masher System compressed disk image", "DMS archive data"],
	program  : "unar"
};
