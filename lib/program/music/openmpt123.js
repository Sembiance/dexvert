"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://lib.openmpt.org/libopenmpt/",
	gentooPackage : "media-sound/openmpt123",
	bruteUnsafe   : true
};

exports.bin = () => "openmpt123";
exports.args = state => (["--batch", "--output", path.join(state.output.dirPath, "outfile.wav"), state.input.filePath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
