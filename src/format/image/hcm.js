"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Hard Color Map",
	ext      : [".hcm"],
	magic    : ["Hard Color Map bitmap"],
	fileSize : 8208
};

exports.converterPriority = ["recoil2png"];
