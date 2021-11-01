"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Vidcom 64",
	website             : "http://fileformats.archiveteam.org/wiki/Vidcom_64",
	ext                 : [".vid"],
	mimeType            : "image/x-vidcom-64",
	magic               : ["Drazpaint (C64) bitmap"], // Shares same magic identifier as Drazpaint
	weakMagic           : true,
	fileSize            : 10050,
	forbidFileSizeMatch : true
};

// nconvert produces clearer output compared to recoil2png
exports.converterPriority = ["nconvert", "recoil2png", "abydosconvert", "view64"];
