"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://github.com/AugusteBonnin/smus2midi",
	gentooPackage  : "media-sound/smus2midi",
	gentooOverlay  : "dexvert"
};

exports.bin = () => "smus2midi";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.cwd, "in.mid"), path.join(state.output.absolute, `${state.input.name}.mid`))(state, p, cb);
