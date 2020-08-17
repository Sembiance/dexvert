"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "IMG Scan",
	ext      : [".rwh", ".rwl", ".raw"],
	filesize : [64000, 128000, 256000]
};

exports.converterPriorty = ["recoil2png"];
