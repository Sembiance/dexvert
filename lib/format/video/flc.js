"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "FLIC FLC Video",
	website  : "http://fileformats.archiveteam.org/wiki/FLIC",
	ext      : [".flc"],
	magic    : ["FLIC FLC video", "FLC animation", "Autodesk Animator Pro FLIC"]
};

exports.preSteps = [state => { state.ffmpegFormat = "flic"; }];
exports.steps = [() => ({program : "ffmpeg"})];
exports.postSteps = [state => { delete state.ffmpegFormat; }];
