"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "FLIC FLC Video",
	website  : "http://fileformats.archiveteam.org/wiki/FLIC",
	ext      : [".flc"],
	magic    : ["FLIC FLC video", "FLC animation", "Autodesk Animator Pro FLIC"]
};

exports.converterPriorty = [{program : "ffmpeg", flags : {ffmpegFormat : "flic"}}, "xanim"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
