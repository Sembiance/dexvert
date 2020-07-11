"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name     : "ISO Disc Image",
	website  : "http://fileformats.archiveteam.org/wiki/ISO_image",
	ext      : [".iso"],
	magic    : ["ISO 9660 CD image", "ISO 9660 CD-ROM filesystem data", "ISO Disk Image File", "Apple ISO9660/HFS hybrid CD image"],
	program  : "uniso",
	priority : C.PRIORITY.TOP
};
