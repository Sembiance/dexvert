"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Microsoft Paint",
	website  : "http://fileformats.archiveteam.org/wiki/MSP_(Microsoft_Paint)",
	ext      : [".msp"],
	magic    : ["Microsoft Paint bitmap", /^M?icrosoft Paint image data/]
};

exports.converterPriority = ["recoil2png", "deark", "nconvert"];
