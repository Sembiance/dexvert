"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Atari ST Floppy Disk Image",
	website  : "http://fileformats.archiveteam.org/wiki/ST_disk_image",
	ext      : [".st"],
	magic    : ["Atari-ST floppy"]
};

exports.converterPriority = ["uniso"];
