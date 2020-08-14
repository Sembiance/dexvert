"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name     : "ZX Spectrum Gigascreen",
	ext      : [".img"],
	// Pretty rare format with weak matching, so let other .img extensions get a higher priority
	priority : C.PRIORITY.LOW
};

exports.converterPriorty = ["recoil2png"];
