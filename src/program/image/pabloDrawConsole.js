"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://picoe.ca/products/pablodraw/",
	gentooPackage : "media-gfx/pablodraw-console",
	gentooOverlay : "dexvert",
	unsafe        : true
};

exports.bin = () => "pablodraw-console";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.png")) => ([`--convert=${inPath}`, `--out=${outPath}`]);
// This can hang at 100% on some files like GRIMMY2.RIP
exports.runOptions = () => ({timeout : XU.MINUTE*2, killSignal : "SIGKILL"});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
