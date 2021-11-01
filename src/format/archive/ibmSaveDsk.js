"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "IBM SaveDskF SKF Disk Image",
	website        : "http://fileformats.archiveteam.org/wiki/LoadDskF/SaveDskF",
	ext            : [".dsk"],
	forbidExtMatch : true,
	magic          : ["IBM SKF disk image", "floppy image data (IBM SaveDskF"]
};

exports.converterPriority = ["7z", "deark"];
