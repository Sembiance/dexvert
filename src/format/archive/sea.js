"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Self Extracting Stuffit Archive",
	website   : "http://fileformats.archiveteam.org/wiki/SIT",
	ext       : [".sea"],
	magic     : ["Macintosh Application (MacBinary)", "Preferred Executable Format"],
	weakMagic : true
};

exports.converterPriority = ["unar"];
