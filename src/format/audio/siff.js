"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Beam Software SIFF Sound",
	website : "http://fileformats.archiveteam.org/wiki/SIFF",
	ext     : [".son"],
	magic   : ["Beam Software SIFF sound"],
	notes   : XU.trim`
		The .son test files are technically supported by libavformat and ffmpeg/cvlc, yet it often produces very distored WAVs.
		My hunch is the decompression algo doesn't quite work with my particular test SIFF files. I couldn't locate ANY OTHER converters.`
};

exports.converterPriority = [{program : "ffmpeg", flags : {ffmpegFormat : "siff"}}];

