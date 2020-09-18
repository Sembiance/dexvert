"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "NEOchrome Animation",
	website  : "http://fileformats.archiveteam.org/wiki/NEOchrome_Animation",
	ext      : [".ani"],
	magic    : ["Atari NEOchrome animation"]
};

exports.steps = [() => ({program : "deark", stateFlags : {dearkJoinFrames : true}})];
