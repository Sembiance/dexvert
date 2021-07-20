"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Video Master Film",
	website : "http://fileformats.archiveteam.org/wiki/Video_Master_Film",
	ext     : [".flm", ".vid", ".vsq"],
	magic   : ["Video Master Film"]
};

exports.converterPriorty = [{program : "deark", flags : {dearkJoinFrames : true}}];
