"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Kyss KYG",
	website  : "http://fileformats.archiveteam.org/wiki/KYG",
	ext      : [".kyg"],
	magic    : ["KYG bitmap"],
	mimeType : "image/x-kyss-graphics"
};

exports.converterPriority = ["abydosconvert"];
