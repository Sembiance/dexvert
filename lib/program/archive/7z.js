"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "http://p7zip.sourceforge.net/",
	gentooPackage  : "app-arch/p7zip",
	gentooUseFlags : "pch",
	unsafe    : true
};

exports.bin = () => "7z";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["x", `-o${outPath}`, inPath]);
