"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Nokia Over the Air Bitmap",
	website  : "http://fileformats.archiveteam.org/wiki/OTA_bitmap",
	ext      : [".otb"]
};

exports.converterPriorty = ["convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
