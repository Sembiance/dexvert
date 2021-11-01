"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "MSX BASIX Graphic",
	website  : "http://fileformats.archiveteam.org/wiki/MSX_BASIC_graphics",
	ext      : [".sc2", ".grp", ".sc3", ".sc4", ".sc5", ".ge5", ".s15", ".sc6", ".s16", ".sc7", ".ge7", ".s17", ".sc8", ".ge8", ".s18", ".sca", ".s1a", ".scc", ".srs", ".yjk", ".s1c"],
	magic    : ["MSX BASIC Graphics bitmap", "MSX SC2/GRP", "MSX GE5/GE6", "MSX screen 7-12"],
	fileSize : {".sc2,.grp" : [14343, 16391]}
};

exports.converterPriority = ["recoil2png"];
