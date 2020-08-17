"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "IMG Scan",
	ext      : [".rwl", ".raw", ".rwh"],
	filesize : {".rwl" : 64000, ".raw" : 128000, ".rwh" : 256000}
};

exports.converterPriorty = ["recoil2png"];
