"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/mdbtools/mdbtools",
	gentooPackage : "app-office/mdbtools"
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "unmdb.js");
exports.args = (state, p, r, inPath=state.input.absolute, outPath=state.output.dirPath) => ([...(state.verbose>=2 ? ["--verbose"] : ""), inPath, outPath]);
