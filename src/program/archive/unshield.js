"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/twogood/unshield",
	gentooPackage : "app-arch/unshield"
};

exports.bin = () => "unshield";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["-d", outPath, "x", inPath]);
