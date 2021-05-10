"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://www.exelana.com/techie/c/ttdecomp.html",
	gentooPackage : "app-arch/ttdecomp",
	gentooOverlay : "dexvert"
};

exports.bin = () => "ttdecomp";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile")) => ([inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, state.input.name))(state, p, cb);
