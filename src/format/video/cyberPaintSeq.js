"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Cyber Paint Sequence",
	website  : "http://fileformats.archiveteam.org/wiki/Cyber_Paint_Sequence",
	ext      : [".seq"],
	magic    : ["Cyber Paint Sequence"]
};

exports.converterPriority = ["seq2mp4"];
