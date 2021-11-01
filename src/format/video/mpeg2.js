"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "MPEG-2",
	website  : "http://fileformats.archiveteam.org/wiki/MPEG-2",
	ext      : [".mpg", ".mp2", ".mpeg", ".m2v"],
	mimeType : "video/mpeg",
	magic    : ["MPEG-2 Elementary Stream", "MPEG-2 Program Stream", "MPEG sequence, v2"]
};

exports.converterPriority = ["ffmpeg", "xanim"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
