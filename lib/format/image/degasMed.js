"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Degas Medium Resolution Picture",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pc2"],
	mimeType : "image/x-pc2",
	magic    : ["DEGAS med-res compressed bitmap"]
};

exports.converterPriorty = ["nconvert", "abydos"];
