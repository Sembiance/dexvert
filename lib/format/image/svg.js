"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Scalable Vector Graphics",
	website   : "http://fileformats.archiveteam.org/wiki/Scalable_Vector_Graphics",
	ext       : [".svg", ".svgz"],
	mimeType  : "image/svg+xml",
	magic     : ["SVG Scalable Vector Graphics image"],
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
