"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Mamut RYS",
	website   : "http://fileformats.archiveteam.org/wiki/Mamut",
	ext       : [".rys"],
	magic     : ["Truevision TGA"],
	weakMagic : true
};

exports.converterPriorty = ["recoil2png"];
