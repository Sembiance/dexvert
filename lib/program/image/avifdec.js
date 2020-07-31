"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/AOMediaCodec/libavif",
	gentooPackage : "media-libs/libavif",
	gentooOverlay : "dexvert"
};

exports.bin = () => "avifdec";
exports.args = state => ([state.input.filePath, path.join(state.output.dirPath, "outfile.png")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
