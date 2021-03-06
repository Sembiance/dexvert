"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Picasso 64",
	website             : "http://fileformats.archiveteam.org/wiki/Picasso_64",
	ext                 : [".p64"],
	mimeType            : "image/x-picasso-64",
	magic               : ["Picasso 64 Image"],
	weakMagic           : true,
	trustMagic          : true,
	fileSize            : 10050,
	forbidFileSizeMatch : true
};

exports.converterPriorty = ["abydosconvert", "nconvert", "recoil2png", "view64"];
