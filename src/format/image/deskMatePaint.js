"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "DeskMate Paint",
	website : "http://fileformats.archiveteam.org/wiki/DeskMate_Paint",
	ext     : [".pnt"],
	magic   : ["DeskMate Paint image"]
};

exports.converterPriority = ["deark", "recoil2png"];
