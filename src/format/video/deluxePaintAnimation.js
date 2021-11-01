"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "DeluxePaint Animation",
	website : "http://fileformats.archiveteam.org/wiki/DeluxePaint_Animation",
	ext     : [".anm"],
	magic   : ["DeluxePaint Animation"],
	notes   : "Sample file HORSE.ANM doesn't convert for some reason"
};

exports.converterPriority = [{program : "ffmpeg", flags : {ffmpegFormat : "anm"}}];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
