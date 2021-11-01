"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://github.com/OmniBlade/isextract",
	gentooPackage  : "app-arch/isextract"
};

exports.bin = () => "isextract";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["x", inPath, outPath]);
exports.runOptions = () => ({timeout : XU.MINUTE*2});
