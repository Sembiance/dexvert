"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");
	

exports.meta =
{
	name     : "RIP Icon",
	ext      : [".icn"],
	priority : C.PRIORITY.HIGH
};

exports.converterPriority = [{ program : "deark", flags : {dearkModule : "ripicon"} }];
