"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "PETSCII Screen Code Sequence",
	website  : "http://fileformats.archiveteam.org/wiki/PETSCII",
	ext      : [".seq"],
	mimeType : "text/x-petscii-sequence",
	unsafe   : true
};

exports.converterPriorty = ["abydosconvert"];
