"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Koala Microillustrator",
	website : "http://fileformats.archiveteam.org/wiki/Koala_MicroIllustrator",
	ext     : [".pic"],
	magic   : ["Koala Micro Illustrator bitmap"],
	notes   : "APOLLO.PIC and STARWAR.PIC don't seem to be handled by recoil."
};

// Sometimes rambrandt rm4 files are identified as Koala, while similar, they are not the same
// But they are similar enough that recoil2png will convert it with a .pic extension, poorly
exports.idCheck = state => state.input.ext.toLowerCase()!==".rm4";

exports.converterPriorty = ["recoil2png", "view64"];
