"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "Scalable Vectory Graphics",
	website       : "http://fileformats.archiveteam.org/wiki/Scalable_Vector_Graphics",
	ext           : [".svg", ".svgz"],
	mimeType      : "image/svg+xml",
	magic         : ["SVG Scalable Vector Graphics image"],
	browserNative : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
