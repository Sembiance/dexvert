"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.ghostscript.com/download/gpcldnld.html",
	gentooPackage : "app-text/ghostpcl-bin",
	gentooOverlay : "dexvert"
};

exports.bin = () => "gpcl6";
exports.args = state => ([`-sOutputFile=${path.join(state.output.dirPath, "outfile.pdf")}`, "-sDEVICE=pdfwrite", "-dNOPAUSE", state.input.filePath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.pdf"), path.join(state.output.absolute, `${state.input.name}.pdf`))(state, p, cb);
