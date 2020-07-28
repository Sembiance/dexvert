"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/adplug/adplay-unix",
	gentooPackage : "media-sound/adplay"
};

exports.bin = () => "adplay";
exports.args = state => (["-O", "disk", "-d", "outfile.wav", state.input.filePath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.cwd, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
