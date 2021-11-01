"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Milti Palette Picture",
	website  : "http://fileformats.archiveteam.org/wiki/Multi_Palette_Picture",
	ext      : [".mpp"],
	mimeType : "image/x-multi-palette-picture",
	magic    : ["Multi Palette Picture bitmap"]
};

exports.converterPriority = ["recoil2png", "abydosconvert"];
