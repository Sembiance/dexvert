"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://gregory.kokanosky.free.fr/v4/linux/nrg2iso.en.html",
	gentooPackage : "app-cdr/nrg2iso"
};

exports.bin = () => "nrg2iso";
exports.args = (state, p, inPath=state.input.filePath, outPath=path.join(state.cwd, "outfile.iso")) => ([inPath, outPath]);
