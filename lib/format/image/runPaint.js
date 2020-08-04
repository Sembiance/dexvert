"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "RUN Paint",
	website   : "http://fileformats.archiveteam.org/wiki/RUN_Paint",
	ext       : [".rpm"],
	magic     : ["Koala Paint"],	// Shares magic with Koala Paint
	weakMagic : true
};

exports.converterPriorty = ["recoil2png", "nconvert"];
