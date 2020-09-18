"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.ansilove.org/",
	gentooPackage : "media-gfx/ansilove",
	gentooOverlay : "dexvert",
	bruteUnsafe   : true
};

exports.bin = () => "ansilove";
exports.args = (state, p, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.png")) => ([...(state.ansiloveType ? ["-t", state.ansiloveType] : []), "-S", "-i", "-o", outPath, inPath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))(state, p, cb);
