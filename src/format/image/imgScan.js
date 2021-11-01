"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "IMG Scan",
	ext      : [".rwl", ".raw", ".rwh"],
	fileSize : {".rwl" : 64000, ".raw" : 128000, ".rwh" : 256000}
};

exports.converterPriority = ["recoil2png"];
