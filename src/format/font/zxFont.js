"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "ZX Spectrum Font",
	ext                 : [".ch4", ".ch6", ".ch8"],
	fileSize            : 2048,
	forbidFileSizeMatch : true
};

exports.steps = [() => ({program : "recoil2png"})];
