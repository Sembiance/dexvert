"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Apple IIGS SH3/SHR",
	ext                 : [".sh3", ".shr"],
	fileSize            : 38400,
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
