"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.xnview.com/en/nconvert/",
	gentooPackage : "media-gfx/nconvert",
	gentooOverlay : "dexvert"
};

exports.bin = () => "nconvert";
exports.args = state => (["-out", "png", "-o", path.join(state.output.dirPath, "outfile.png"), state.input.filePath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
