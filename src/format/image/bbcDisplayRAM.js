"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "BBC Display RAM Dump",
	fileSize    : 1000,
	mimeType    : "image/x-bbc-micro-screendump",
	unsupported : true,
	notes       : "While supported, due to no extension and no magic, it's impossible to accurately detect. Abydos will convert invalid files and and produce a garbled image, thus not able to just try a conversion and see."
};

//exports.converterPriority = ["abydosconvert"];
