"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Degas High Resolution Picture",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pc3"],
	mimeType : "image/x-pc3",
	magic    : ["DEGAS hi-res compressed bitmap"]
};

exports.converterPriorty = ["nconvert", "abydos"];
