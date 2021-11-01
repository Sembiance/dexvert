"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "True Colour Sprites",
	website     : "http://fileformats.archiveteam.org/wiki/Spooky_Sprites",
	ext         : [".trs"],
	magic       : ["True Colour Sprites bitmap"],
	mimeType    : "image/x-spooky-sprites"
};

exports.converterPriority = ["abydosconvert"];
