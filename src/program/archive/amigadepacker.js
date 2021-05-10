"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://zakalwe.fi/~shd/foss/amigadepacker/",
	gentooPackage : "app-arch/amigadepacker",
	gentooOverlay : "dexvert"
};

exports.bin = () => "amigadepacker";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile")) => (["-o", outPath, inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, state.input.name))(state, p, cb);
