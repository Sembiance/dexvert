"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/fuzziqersoftware/resource_dasm",
	gentooPackage : "app-arch/resource-dasm",
	gentooOverlay : "dexvert"
};

exports.bin = () => "hypercard_dasm";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => ([inPath, outPath]);
