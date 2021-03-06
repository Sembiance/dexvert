"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "FLIC FLI Video",
	website  : "http://fileformats.archiveteam.org/wiki/FLIC",
	ext      : [".fli"],
	magic    : ["FLIC FLI video", "FLI animation", "AutoDesk FLIC Animation"]
};

exports.converterPriorty = [{program : "ffmpeg", flags : {ffmpegFormat : "flic"}}, "xanim"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
