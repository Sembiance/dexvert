"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "AmigaBASIC Source Code",
	ext         : [".bas"],
	magic       : ["AmigaBASIC source"],
	bruteUnsafe : true
};

exports.steps = [() => ({program : "ab2ascii"})];
