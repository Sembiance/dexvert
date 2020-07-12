"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Genus Graphics Library Compressed Archive",
	ext     : [".gx", ".gxl"],
	magic   : ["Genus Graphics Library"],
	program : "unpcx"
};

exports.steps = () => ([(state, p, cb) => p.util.wine.run({cmd : "unpcxgx.exe", args : state.input.absolute, cwd : state.output.absolute})(state, p, cb)]);
