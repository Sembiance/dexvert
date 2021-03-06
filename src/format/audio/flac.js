"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Free Lossless Audio Codece",
	website   : "http://fileformats.archiveteam.org/wiki/FLAC",
	ext       : [".flac"],
	mimeType  : "audio/x-flac",
	magic     : ["FLAC audio bitstream data", "FLAC lossless compressed audio", "FLAC (Free Lossless Audio Codec)"],
	untouched : true
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
