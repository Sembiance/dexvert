"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/mikmod2wav",
	gentooPackage : "media-sound/mikmod2wav",
	gentooOverlay : "dexvert",
	bruteUnsafe   : true
};

exports.bin = () => "mikmod2wav";
exports.args = state => (["--limitSeconds", "900", state.input.filePath, path.join(state.output.dirPath, "outfile.wav")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
