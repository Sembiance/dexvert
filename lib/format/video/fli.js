"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "FLIC FLI Video",
	website  : "http://fileformats.archiveteam.org/wiki/FLIC",
	ext      : [".fli"],
	magic    : ["FLIC FLI video", "FLI animation", "AutoDesk FLIC Animation"]
};

exports.preSteps = [state => { state.ffmpegFormat = "flic"; }];
exports.steps = [() => ({program : "ffmpeg"})];
exports.postSteps = [state => { delete state.ffmpegFormat; }];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
