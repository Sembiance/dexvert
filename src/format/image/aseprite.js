"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Asperite",
	website  : "https://www.aseprite.org/",
	ext      : [".ase", ".aseprite"],
	mimeType : "image/x-aseprite"
};

exports.converterPriority = ["abydosconvert"];
