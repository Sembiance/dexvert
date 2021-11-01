"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/kyz/amostools/",
	gentooPackage : "dev-lang/amostools",
	gentooOverlay : "dexvert"
};

exports.bin = () => "dumpamos";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.cwd = state => state.output.absolute;
