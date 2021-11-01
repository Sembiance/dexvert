"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name          : "Acorn (RISC OS) Sprite",
	website       : "http://fileformats.archiveteam.org/wiki/Acorn_Sprite",
	ext           : [".acorn"],
	magic         : ["GLS_BINARY_LSB_FIRST", "GLS_BINARY_MSB_FIRST"],
	priority      : C.PRIORITY.LOW,
	untrustworthy : true
};

exports.converterPriority = [{ program : "deark", flags : {dearkModule : "rosprite"} }, "nconvert"];
