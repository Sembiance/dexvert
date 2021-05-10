"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://djvu.sourceforge.net/",
	gentooPackage : "app-text/djvu"
};

exports.bin = () => "ddjvu";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.pdf")) => (["-format=pdf", inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.pdf"), path.join(state.output.absolute, `${state.input.name}.pdf`))(state, p, cb);
