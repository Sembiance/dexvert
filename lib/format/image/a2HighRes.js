"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Apple II High Res",
	ext                 : [".hgr"],
	fileSize            : 8192,
	bruteUnsafe         : true, // recoil2png will take any 8k file and turn it into a garbage PNG
	forbidFileSizeMatch : true
};

exports.converterPriorty = ["recoil2png"];
