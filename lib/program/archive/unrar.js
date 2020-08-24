"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://www.rarlab.com/rar_add.htm",
	gentooPackage : "app-arch/unrar"
};

exports.bin = () => "unrar";
exports.args = (state, p, inPath=state.input.filePath, outPath=state.output.dirPath) => (["x", "-p-", inPath, outPath]);
