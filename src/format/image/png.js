"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Portable Network Graphic",
	website   : "http://fileformats.archiveteam.org/wiki/PNG",
	ext       : [".png"],
	mimeType  : "image/png",
	magic     : ["Portable Network Graphics", "PNG image data"],
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
