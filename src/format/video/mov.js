"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Apple QuickTime movie",
	website  : "http://fileformats.archiveteam.org/wiki/MOV",
	ext      : [".mov"],
	mimeType : "video/quicktime",
	magic    : ["Apple QuickTime movie", "QuickTime Movie"]
};

exports.converterPriority = ["ffmpeg", "xanim"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
