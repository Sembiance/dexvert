"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/temisu/ancient_format_decompressor",
	gentooPackage : "app-arch/ancient",
	gentooOverlay : "dexvert"
};

exports.bin = () => "ancient";
exports.args = state => (["decompress", state.input.filePath, path.join(state.output.dirPath, "outfile")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, state.input.name))(state, p, cb);
