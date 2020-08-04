"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Neochrome",
	website  : "http://fileformats.archiveteam.org/wiki/NEOchrome",
	ext      : [".neo"],
	mimeType : "image/x-neo",
	filesize : [32128]
};

exports.converterPriorty = ["nconvert", "abydosconvert"];
