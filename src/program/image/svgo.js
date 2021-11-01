"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website     : "https://www.npmjs.com/package/svgo",
	unsafe : true
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "node_modules", ".bin", "svgo");
exports.args = (state, p, r, inPath=state.input.filePath) => (["--multipass", "--final-newline", inPath]);
