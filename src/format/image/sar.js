"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Saracen Paint",
	website   : "http://fileformats.archiveteam.org/wiki/Saracen_Paint",
	ext       : [".sar"],
	mimeType  : "image/x-saracen-paint",
	magic     : ["Saracen Paint Image"],
	weakMagic : true
};

exports.converterPriority = ["nconvert", "recoil2png", "abydosconvert", "view64"];
