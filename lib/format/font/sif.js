"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Super-IRG",
	ext                 : [".sif"],
	fileSize            : 2048,
	forbidFileSizeMatch : true	// recoil2png will convert any file, so we should only do it if we also have the proper extension
};

exports.steps = [() => ({program : "recoil2png"})];
