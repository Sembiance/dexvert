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

exports.converterPriorty = ["recoil2png"];
