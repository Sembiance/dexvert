"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Animatic Film",
	website  : "http://fileformats.archiveteam.org/wiki/Animatic_Film",
	ext      : [".flm"],
	magic    : ["Animatic Film"]
};

exports.converterPriorty = [{program : "deark", flags : {dearkJoinFrames : true}}];
