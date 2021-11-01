"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Yanagisawa PIC",
	website   : "http://fileformats.archiveteam.org/wiki/PIC_(Yanagisawa)",
	ext       : [".pic"],
	magic     : ["Yanagisawa PIC image file", "PIC bitmap"],
	weakMagic : true
};

exports.converterPriority = ["recoil2png"];
