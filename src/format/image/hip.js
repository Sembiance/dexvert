"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Hard Interlace Picture",
	website : "http://fileformats.archiveteam.org/wiki/Hard_Interlace_Picture",
	ext     : [".hip", "hps"],
	notes   : "Sample file AGA2.HPS converts to just static noise. Not sure if this is an error in recoil2png or a fault in the file or expected output."
};

exports.converterPriority = ["recoil2png"];
