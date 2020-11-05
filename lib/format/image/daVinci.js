"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "DaVinci",
	website  : "http://fileformats.archiveteam.org/wiki/DaVinci",
	ext      : [".img"],
	mimeType : "image/x-davinci"
};

exports.converterPriorty = ["recoil2png", "abydosconvert"];
