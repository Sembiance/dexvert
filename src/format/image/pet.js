"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "PETSCII Editor",
	ext                 : [".pet"],
	fileSize            : 2026,
	forbidFileSizeMatch : true
};

exports.converterPriorty = ["recoil2png"];
