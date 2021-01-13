"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/dexvert/tree/master/dexmagic",
	informational : true
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "dexmagic", "dexmagic");
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.runOptions = () => ({"ignore-stderr" : true});
