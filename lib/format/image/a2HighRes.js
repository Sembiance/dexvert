"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Apple II High Res",
	ext      : [".hgr"],
	filesize : [8192],

	// recoil2png will take any 8k file and turn it into a garbage PNG
	bruteUnsafe         : true,
	forbidFilesizeMatch : true
};

exports.converterPriorty = ["recoil2png"];
