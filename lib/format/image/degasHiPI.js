"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Degas High Resolution Picture (PI)",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pi3"],
	mimeType : "image/x-pi3",
	magic    : ["DEGAS hi-res bitmap"]
};

exports.converterPriorty = ["nconvert", "abydos"];
