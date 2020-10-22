"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name     : "AMOS Picture Packer",
	ext      : [".bin"],
	mimeType : "image/x-amos-picturepacker",
	priority : C.PRIORITY.LOW
};

exports.converterPriorty = ["abydosconvert"];
