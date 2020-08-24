"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/kyz/amostools/",
	gentooPackage : "dev-lang/amostools",
	gentooOverlay : "dexvert"
};

// stackimport creates an 'in.xstk' subdir with all results
exports.bin = () => "dumpamos";
exports.args = (state, p, inPath=state.input.filePath) => ([inPath]);
exports.cwd = state => state.output.absolute;
