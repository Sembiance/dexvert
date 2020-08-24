"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Atari FontMaker",
	ext         : [".fn2"],
	filesize    : 2048
};

exports.steps = [() => ({program : "recoil2png"})];
