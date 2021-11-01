"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "BBC Micro Image",
	ext                 : [".bb0", ".bb1", ".bb2", ".bb4", ".bb5"],
	fileSize            : [10240, 20480],
	forbidFileSizeMatch : true
};

exports.converterPriority = ["recoil2png"];
