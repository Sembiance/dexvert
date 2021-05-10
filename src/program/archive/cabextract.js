"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://www.cabextract.org.uk/",
	gentooPackage : "app-arch/cabextract"
};

exports.bin = () => "cabextract";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["--directory", outPath, "--fix", inPath]);
