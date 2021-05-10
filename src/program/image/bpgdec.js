"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://bellard.org/bpg/",
	gentooPackage : "media-libs/libbpg",
	gentooOverlay : "dexvert"
};

exports.bin = () => "bpgdec";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.png")) => (["-o", outPath, inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
