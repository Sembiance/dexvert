"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Atari FontMaker",
	ext                 : [".fn2", ".fnt", ".fn8"],
	safeExt             : () => ".fn2",
	fileSize            : 2048,
	forbidFileSizeMatch : true
};

exports.steps = [() => ({program : "recoil2png"})];
