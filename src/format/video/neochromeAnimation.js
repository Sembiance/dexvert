"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "NEOchrome Animation",
	website  : "http://fileformats.archiveteam.org/wiki/NEOchrome_Animation",
	ext      : [".ani"],
	magic    : ["Atari NEOchrome animation"]
};

exports.converterPriorty = [{program : "deark", flags : {dearkJoinFrames : true}}];
