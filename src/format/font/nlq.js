"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Daisy-Dot",
	ext   : [".nlq"],
	magic : ["Daisy-Dot NLQ font"],
	notes : "Most of the sample files do not convert with recoil2png. Maybe a different version?"
};

exports.steps = [() => ({program : "recoil2png"})];
