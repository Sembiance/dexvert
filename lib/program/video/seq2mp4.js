"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/seq2mp4",
	gentooPackage : "media-gfx/seq2mp4",
	gentooOverlay : "dexvert"
};

exports.bin = () => "seq2mp4";
exports.args = state => ([state.input.filePath, path.join(state.output.dirPath, "outfile.mp4")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.mp4"), path.join(state.output.absolute, `${state.input.name}.mp4`))(state, p, cb);
