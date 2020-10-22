"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Atari FontMaker",
	ext      : [".fn2"],
	fileSize : 2048
};

exports.steps = [() => ({program : "recoil2png"})];
