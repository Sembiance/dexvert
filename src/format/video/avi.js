"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Audio Video Interleaved Video",
	website  : "http://fileformats.archiveteam.org/wiki/AVI",
	ext      : [".avi"],
	mimeType : "video/avi",
	magic    : ["AVI Audio Video Interleaved", /^RIFF.* data, AVI.* video/, "Audio/Video Interleaved Format"]
};

exports.converterPriorty = ["ffmpeg", "xanim"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
