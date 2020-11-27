"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Shoot Em Up Construction Kit Font",
	ext      : [".g"],
	fileSize : 514,
	notes    : "Only one file format has been located. To prevent false positives it assumes this format is 514 bytes long, always."
};

exports.steps = [() => ({program : "recoil2png"})];
