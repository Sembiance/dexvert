"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Commodore Disk Image",
	website  : "http://fileformats.archiveteam.org/wiki/D64",
	ext      : [".d64", ".d81", ".d71", ".g64"],
	magic    : ["D64 Image", "D81 Image", "G64 GCR-encoded Disk Image Format", "G64 1541 raw disk image"],
	fileSize :
	{
		".d64" : 174848,
		".d81" : 819200
	}
};

exports.converterPriority = ["c1541", "DirMaster"];
