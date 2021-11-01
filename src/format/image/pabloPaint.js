"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "PabloPaint",
	website  : "http://fileformats.archiveteam.org/wiki/PabloPaint",
	ext      : [".pa3", ".ppp"],
	mimeType : "image/x-pablo-packed-picture",
	magic    : ["PabloPaint packed bitmap"]
};

exports.converterPriority = ["recoil2png", "abydosconvert"];
