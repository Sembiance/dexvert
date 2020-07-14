"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Disk Image",
	website : "http://fileformats.archiveteam.org/wiki/Disk_Image_Formats",
	ext     : [".img"],
	magic   : ["Generic PC disk image", "FAT Disk Image"]
};

exports.steps = [() => ({program : "7z"})];
