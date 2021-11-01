"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "JPEG 2000",
	website  : "http://fileformats.archiveteam.org/wiki/JPEG_2000",
	ext      : [".jp2"],
	mimeType : "image/jp2",
	magic    : ["JPEG 2000", "JP2 (JPEG 2000"]
};

exports.converterPriority = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
