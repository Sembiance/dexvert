"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Degas Low Resolution Picture",
	website  : "http://fileformats.archiveteam.org/wiki/DEGAS_image",
	ext      : [".pc1"],
	mimeType : "image/x-pc1",
	magic    : ["DEGAS low-res compressed bitmap"]
};

exports.converterPriorty = ["nconvert", "abydos"];
