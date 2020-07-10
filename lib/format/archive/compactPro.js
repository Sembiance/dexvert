"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name     : "Mac Compact Pro Archive",
	ext      : [".cpt"],
	magic    : ["Mac Compact Pro archive"],
	priority : C.PRIORITY.LOW,
	program  : "unar"
};
