"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/System25/drxtract",
	gentooPackage : "app-arch/drxtract",
	gentooOverlay : "dexvert"
};

exports.bin = () => "undirector";
exports.args = (state, p, inPath=state.input.filePath, outPath=state.output.dirPath) => (["pc", inPath, outPath]);
