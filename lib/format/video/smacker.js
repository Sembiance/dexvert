"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Smacker Video",
	website  : "http://fileformats.archiveteam.org/wiki/Smacker",
	ext      : [".smk"],
	magic    : ["Smacker movie/video (original)", "Smacker Video", /^RAD Game Tools Smacker Multimedia .* frames$/]
};

exports.preSteps = [state => { state.ffmpegFormat = "smk"; }];
exports.steps = [() => ({program : "ffmpeg"})];
exports.postSteps = [state => { delete state.ffmpegFormat; }];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
