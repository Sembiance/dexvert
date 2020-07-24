"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Degas Low Resolution Picture (PI)",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pi1"],
	mimeType : "image/x-pi1"
};

exports.converterPriorty = ["nconvert", "abydos"];
