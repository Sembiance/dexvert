"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "IMG Scan",
	ext     : [".rwh", ".rwl", ".raw"],
	filesize : [state => ({".rwl" : 64000, ".raw" : 128000, ".rwh" : 256000}[state.input.ext.toLowerCase()])]
};

exports.converterPriorty = ["recoil2png"];
