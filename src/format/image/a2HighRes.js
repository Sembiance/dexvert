"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Apple II High Res",
	ext                 : [".hgr"],
	fileSize            : 8192,
	forbidFileSizeMatch : true,
	unsafe              : true
};

exports.converterPriority = ["recoil2png"];
