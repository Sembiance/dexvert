"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/adplug/adplay-unix",
	gentooPackage : "media-sound/adplay",
	bruteUnsafe   : true
};

exports.bin = () => "adplay";
exports.args = (state, p, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => (["-O", "disk", "-d", outPath, inPath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
