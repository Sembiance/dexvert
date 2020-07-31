"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "JPEG Network Graphics",
	website  : "http://fileformats.archiveteam.org/wiki/JNG",
	ext      : [".jng"],
	mimeType : "image/x-jng",
	magic    : ["JPEG Network Graphics", "JNG video data"]
};

exports.converterPriorty = ["convert", "nconvert", "abydosconvert"];
