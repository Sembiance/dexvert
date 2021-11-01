"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.ghostscript.com/download/gpcldnld.html",
	gentooPackage : "app-text/ghostpcl-bin",
	gentooOverlay : "dexvert",
	unsafe   : true
};

exports.bin = () => "gpcl6";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.pdf")) => ([`-sOutputFile=${outPath}`, "-sDEVICE=pdfwrite", "-dNOPAUSE", inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.pdf"), path.join(state.output.absolute, `${state.input.name}.pdf`))(state, p, cb);
