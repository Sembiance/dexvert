"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://github.com/Sembiance/dexvert"
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "stosBAS2txt.js");
exports.args = (state, p, r, inPath=state.input.absolute, outPath=path.join(state.output.absolute, `${state.input.name}.txt`)) => ([...(state.verbose>=2 ? ["--verbose"] : ""), inPath, outPath]);
