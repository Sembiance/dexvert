"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "CDXL",
	website     : "http://fileformats.archiveteam.org/wiki/CDXL",
	ext         : [".cdxl", ".xl"],
	magic       : ["Amiga CDXL video"]
};

exports.converterPriority = [{program : "ffmpeg", flags : {ffmpegFormat : "cdxl"}}];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
