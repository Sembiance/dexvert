"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Silicon Graphics IRIX Movie",
	website  : "http://fileformats.archiveteam.org/wiki/SGI_movie",
	ext      : [".mv", ".movie", ".sgi"],
	magic    : ["SGI video", "Silicon Graphics movie file"]
};

exports.converterPriorty = ["ffmpeg", "xanim"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
