"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name     : "Artist by David Eaton",
	ext      : [".art"],
	priority : C.PRIORITY.LOW
};

exports.converterPriority = ["recoil2png"];
