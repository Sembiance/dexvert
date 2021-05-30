"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://picoe.ca/products/pablodraw/",
	gentooPackage : "media-gfx/pablodraw-console",
	gentooOverlay : "dexvert"
};

exports.bin = () => "pablodraw-console";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.png")) => ([`--convert=${inPath}`, `--out=${outPath}`]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
