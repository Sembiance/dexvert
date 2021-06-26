"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://view64.sourceforge.net/",
	gentooPackage : "media-gfx/view64",
	gentooOverlay : "dexvert",
	unsafe        : true
};

exports.bin = () => "view64pnm";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.redirectOutput = state => path.join(state.cwd, "outfile.pnm");
exports.post = (state, p, r, cb) => p.util.program.run("convert", {argsd : ["outfile.pnm"]})(state, p, cb);
