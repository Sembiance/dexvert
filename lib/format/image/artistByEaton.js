"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name     : "Artist by David Eaton",
	ext      : [".art"],
	priority : C.PRIORITY.LOW
};

exports.converterPriorty = ["recoil2png"];
