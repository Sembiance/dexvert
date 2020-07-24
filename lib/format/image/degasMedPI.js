"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Degas Medium Resolution Picture (PI)",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pi2"],
	mimeType : "image/x-pi2",
	magic    : ["DEGAS med-res bitmap"]
};

exports.converterPriorty = ["nconvert", "abydos"];
