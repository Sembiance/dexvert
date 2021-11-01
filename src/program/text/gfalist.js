"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/gfalist",
	gentooPackage : "dev-lang/gfalist",
	gentooOverlay : "dexvert"
};

exports.bin = () => "gfalist";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-f", inPath]);
exports.redirectOutput = state => path.join(state.output.absolute, `${state.input.name}.bas`);
