"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "http://sox.sourceforge.net",
	gentooPackage  : "media-sound/sox",
	gentooUseFlags : "alsa amr encode flac id3tag mad ogg openmp png sndfile twolame wavpack",
	informational  : true
};

exports.bin = () => "soxi";
exports.args = state => ([state.input.filePath]);
