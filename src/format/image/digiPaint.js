"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Digi Paint",
	website  : "http://fileformats.archiveteam.org/wiki/Digi_Paint",
	ext      : [".ap3", ".apv", ".dgi", ".dgp", ".ilc", ".esc", ".pzm", ".g09", ".bg9"],
	fileSize : [15360, 15362, 15872]
};

exports.converterPriorty = ["recoil2png"];
