"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Draz Paint",
	website   : "http://fileformats.archiveteam.org/wiki/Drazpaint",
	ext       : [".drz", ".drp"],
	mimeType  : "image/x-draz-paint",
	magic     : ["Drazpaint"],
	weakMagic : true
};

exports.converterPriorty = ["abydosconvert", "nconvert", "recoil2png", "view64"];
