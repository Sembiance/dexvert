"use strict";
const XU = require("@sembiance/xu"),
	psMeta = require("../document/ps.js").meta;

exports.meta =
{
	name           : "HP Printer Command Language",
	website        : "http://fileformats.archiveteam.org/wiki/PCL",
	ext            : [".pcl", ".prn"],
	forbiddenMagic : psMeta.magic, // Often Postscript files are mis-identified as PCL files. If it ends in .ps just never allow a match
	mimeType       : "application/vnd.hp-PCL",
	magic          : ["HP Printer Command Language", "HP PCL printer data"],
	unsafe         : true
};

exports.converterPriority = ["gpcl6"];
