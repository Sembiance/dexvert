"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "FLIP Image",
	website   : "http://fileformats.archiveteam.org/wiki/FLIP",
	ext       : [".fbi"],
	magic     : ["SysEx File"],
	weakMagic : true
};

exports.converterPriority = ["recoil2png"];
