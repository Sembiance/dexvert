"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Interchange File Format Animation",
	website  : "http://fileformats.archiveteam.org/wiki/ANIM",
	ext      : [".anim", ".anm", ".sndanim"],
	magic    : ["IFF data, ANIM animation", "IFF ANIM"]
};

exports.preSteps = [state => { state.ffmpegFormat = "iff"; }];
exports.steps = [() => ({program : "ffmpeg"})];
exports.postSteps = [state => { delete state.ffmpegFormat; }];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
