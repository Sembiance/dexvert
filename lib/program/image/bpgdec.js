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
exports.args = state => (["-o", path.join(state.output.dirPath, "outfile.png"), state.input.filePath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
