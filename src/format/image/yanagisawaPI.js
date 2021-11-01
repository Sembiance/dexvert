"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "MSX2 Yanagisawa PI",
	ext   : [".pi"],
	magic : [/Yanagisawa Pi /]
};

exports.converterPriority = ["recoil2png"];
