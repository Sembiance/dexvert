"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "NEOchrome Animation",
	website  : "http://fileformats.archiveteam.org/wiki/NEOchrome_Animation",
	ext      : [".ani"],
	magic    : ["Atari NEOchrome animation"]
};

exports.preSteps = [state => { state.dearkJoinFrames = true; }];
exports.steps = [() => ({program : "deark"})];
exports.postSteps = [state => { delete state.dearkJoinFrames; }];
