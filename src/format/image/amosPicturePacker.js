"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name     : "AMOS Picture Packer",
	ext      : [".bin"],
	mimeType : "image/x-amos-picturepacker",
	priority : C.PRIORITY.LOW
};

exports.converterPriority = ["abydosconvert"];
