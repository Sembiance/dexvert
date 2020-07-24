"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/abydosconvert",
	gentooPackage : "media-gfx/abydosconvert",
	gentooOverlay : "dexvert"
};

exports.bin = () => "abydosconvert";
exports.args = (state, p) => ([p.format.meta.mimeType, state.input.filePath, path.join(state.output.dirPath, "outfile.png")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
