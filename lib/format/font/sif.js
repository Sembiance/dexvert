"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Super-IRG",
	ext      : [".sif"],
	filesize : 2048
};

exports.steps = [() => ({program : "recoil2png"})];
