"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "MPEG-1",
	website  : "http://fileformats.archiveteam.org/wiki/MPEG-1",
	ext      : [".mpg", ".mp1", ".mpeg", ".m1v"],
	mimeType : "video/mpeg",
	magic    : ["MPEG-1 Elementary Stream", "MPEG-1 Program Stream", "MPEG sequence, v1"]
};

exports.steps = [() => ({program : "ffmpeg"})];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
