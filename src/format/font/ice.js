"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name : "Interlace Character Editor",
	ext  : [".ice"]
};

exports.steps = [() => ({program : "recoil2png"})];
