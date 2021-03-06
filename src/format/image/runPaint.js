"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name       : "RUN Paint",
	website    : "http://fileformats.archiveteam.org/wiki/RUN_Paint",
	ext        : [".rpm", ".rph", ".rpo"],
	magic      : ["Koala Paint"], // Shares magic with Koala Paint
	weakMagic  : true,
	trustMagic : true, // Koala Paint is normally untrustworthy, but we trust it here
	fileSize   : [10003, 10006]

};

exports.converterPriorty = ["recoil2png", "nconvert", "view64"];
