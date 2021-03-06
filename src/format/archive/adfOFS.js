"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Amiga Disk Format (OFS)",
	website  : "http://fileformats.archiveteam.org/wiki/ADF_(Amiga)",
	ext      : [".adf"],
	fileSize : 901120,
	magic    : ["Amiga Disk image File (OFS)", "Amiga DOS disk"],
	notes    : XU.trim`
		Some Amiga disks (such as voyager.adf) are non DOS (NDOS) disks with custom filesystems.
		These cannot be mounted by the amiga nor extracted with unar/unadf/adf-extractor
		These are custom disk formats that demo and game coders came up with to squeeze data out of em.
		Sadly there isn't really any way to extract files from these disks, as they might not even have a concept of files at all.`
};

exports.converterPriorty = ["unadf", "extract-adf", "unar", "IsoBuster"];
