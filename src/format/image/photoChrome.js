"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "PhotoChrome",
	website  : "http://fileformats.archiveteam.org/wiki/PhotoChrome",
	ext      : [".pcs"],
	mimeType : "image/x-photochrome-screen",
	magic    : ["PhotoChrome bitmap"]
};

exports.converterPriorty = ["recoil2png", "abydosconvert"];
