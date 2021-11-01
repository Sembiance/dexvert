"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Electronika BK PIC",
	ext                 : [".pic"],
	fileSize            : 16384,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
