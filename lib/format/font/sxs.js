"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Atari SXS Font",
	ext      : [".sxs"],
	filesize : 1030
};

exports.steps = [() => ({program : "recoil2png"})];
