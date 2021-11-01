"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Alias PIX Image",
	website  : "http://fileformats.archiveteam.org/wiki/Alias_PIX",
	ext      : [".pix", ".alias", ".img", ".als"],
	mimeType : "image/x-alias-pix",
	magic    : ["Alias PIX"]
};

exports.converterPriority = ["nconvert"];
