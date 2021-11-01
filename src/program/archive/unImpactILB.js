"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://github.com/Sembiance/dexvert"
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "unImpactILB.js");
exports.args = (state, p, r, inPath=state.input.absolute, outPath=state.output.dirPath) => ([...(state.verbose>=2 ? ["--verbose"] : ""), inPath, outPath]);
