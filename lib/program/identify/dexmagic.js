"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/Sembiance/dexmagic",
	informational : true
};

exports.bin = () => "dexmagic";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.runOptions = () => ({"ignore-stderr" : true});
