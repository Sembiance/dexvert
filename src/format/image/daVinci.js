"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "DaVinci",
	website  : "http://fileformats.archiveteam.org/wiki/DaVinci",
	ext      : [".img"],
	mimeType : "image/x-davinci"
};

// abydosconvert will also convert these, but unlike recoil2png, abydos will take any garbage file and produce garbage output
exports.converterPriority = ["recoil2png"];
