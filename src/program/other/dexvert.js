"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://github.com/Sembiance/dexvert"
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "dexvert");
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["--useTmpOutputDir", inPath, outPath]);
