"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Centauri Logo Editor",
	website             : "http://fileformats.archiveteam.org/wiki/Centauri_Logo_Editor",
	ext                 : [".cle"],
	magic               : ["Koala Paint"], // Not actually Koala Paint, just shares the same magic
	weakMagic           : true,
	trustMagic          : true,
	fileSize            : 8194,
	forbidFileSizeMatch : true

};

exports.converterPriority = ["recoil2png", "view64"];
