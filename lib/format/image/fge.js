"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name      : "Floor Designer",
	website   : "http://fileformats.archiveteam.org/wiki/Floor_Designer",
	ext       : [".fge"],
	magic     : ["Atari XE Executable"],
	weakMagic : true
};

exports.converterPriorty = ["recoil2png"];
