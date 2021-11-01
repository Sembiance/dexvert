"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "ZOOM Disk Image",
	ext         : [".zom"],
	magic       : ["Zoom compressed disk image"],
	unsupported : true,
	notes       : "No known modern converter/extractor. Amiga program ZOOM to create and write to floppy: http://aminet.net/package/misc/fish/fish-0459"
};
