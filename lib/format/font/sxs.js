"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Atari SXS Font",
	ext                 : [".sxs"],
	fileSize            : 1030,
	forbidFileSizeMatch : true	// recoil2png will convert any file, so we should only do it if we also have the proper extension
};

exports.steps = [() => ({program : "recoil2png"})];
