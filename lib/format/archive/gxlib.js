"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Genus Graphics Library Compressed Archive",
	ext     : [".gx", ".gxl"],
	magic   : ["Genus Graphics Library"]
};

exports.steps = [(state, p) => p.util.wine.run({cmd : "unpcxgx.exe", args : state.input.absolute, cwd : state.output.absolute})];
