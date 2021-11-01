"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/gzaffin/eupmini",
	gentooPackage : "media-sound/eupmini",
	gentooOverlay : "dexvert",
	unsafe        : true
};

exports.bin = () => "eupplay";
exports.runOptions = () => ({env : {SDL_AUDIODRIVER : "disk"}});
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => (["-o", outPath, inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
