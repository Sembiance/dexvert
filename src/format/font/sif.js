"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Super-IRG",
	ext                 : [".sif"],
	fileSize            : 2048,
	forbidFileSizeMatch : true
};

exports.steps = [() => ({program : "recoil2png"})];
