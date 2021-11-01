"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Tobias Richter Fullscreen Slideshow",
	website  : "http://fileformats.archiveteam.org/wiki/Tobias_Richter_Fullscreen_Slideshow",
	ext      : [".pci"],
	mimeType : "image/x-tobias-richter-fullscreen-slideshow"
};

exports.converterPriority = ["recoil2png", "abydosconvert"];
