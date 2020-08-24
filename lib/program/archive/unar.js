"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://unarchiver.c3.cx/",
	gentooPackage : "app-arch/unar"
};

exports.bin = () => "unar";
exports.args = (state, p, inPath=state.input.filePath, outPath=state.output.dirPath) => (["-f", "-D", "-o", outPath, inPath]);
