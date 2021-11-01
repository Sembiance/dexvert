"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Logo-Painter",
	website   : "http://fileformats.archiveteam.org/wiki/Logo-Painter",
	ext       : [".lp3"],
	magic     : ["Picasso 64 Image"],
	weakMagic : true
};

exports.converterPriority = ["recoil2png", "view64"];
