"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "http://xmp.sourceforge.net/",
	gentooPackage  : "media-sound/xmp",
	gentooOverlay  : "dexvert",
	gentooUseFlags : "alsa",
	bruteUnsafe    : true
};

exports.bin = () => "xmp";
exports.args = state => (["-o", path.join(state.output.dirPath, "outfile.wav"), state.input.filePath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
