"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://gitlab.freedesktop.org/xorg/app/bdftopcf",
	gentooPackage : "x11-apps/bdftopcf"
};

exports.bin = () => "bdftopcf";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.pcf")) => (["-o", outPath, inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.pcf"), path.join(state.output.absolute, `${state.input.name}.pcf`))(state, p, cb);
