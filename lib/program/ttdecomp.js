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
exports.args = state => ([state.input.filePath, path.join(state.output.dirPath, "outfile")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, state.input.name))(state, p, cb);
