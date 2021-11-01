"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Hi-Eddi",
	website  : "http://fileformats.archiveteam.org/wiki/Hi-Eddi",
	ext      : [".hed"],
	mimeType : "image/x-hi-eddi",
	fileSize : 9218
};

exports.converterPriority = ["nconvert", "abydosconvert", "view64"];
