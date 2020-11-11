"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Shoot Em Up Construction Kit Font",
	ext                 : [".g"],
	fileSize            : 514,
	notes               : "Only one file format has been located. To prevent false positives it assumes this format is 514 bytes long, always.",
	forbidFileSizeMatch : true	// recoil2png will convert any file, so we should only do it if we also have the proper extension
};

exports.steps = [() => ({program : "recoil2png"})];
