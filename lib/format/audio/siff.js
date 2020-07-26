"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Beam Software SIFF Sound",
	website     : "http://fileformats.archiveteam.org/wiki/SIFF",
	ext         : [".son"],
	magic       : ["Beam Software SIFF sound"],
	unsupported : true,
	notes       : XU.trim`
		The .son files are technically supported by libavformat and ffmpeg/cvlc, yet for these files the WAVs they procude are very distorted
		My hunch is the decompression algo doesn't quite work with these particular SIFF files. I couldn't locate ANY OTHER converters.`
};
