"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Vidcom 64",
	website  : "http://fileformats.archiveteam.org/wiki/Vidcom_64",
	ext      : [".vid"],
	mimeType : "image/x-vidcom-64",
	magic    : ["Drazpaint (C64) bitmap"],	// Shares same magic identifier as Drazpaint
	filesize : [10050]
};

exports.converterPriorty = ["nconvert", "recoil2png", "abydosconvert"];
