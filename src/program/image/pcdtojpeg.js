"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://pcdtojpeg.sourceforge.io/Home.html",
	gentooPackage : "media-gfx/pcdtojpeg",
	gentooOverlay : "dexvert"
};

exports.bin = () => "pcdtojpeg";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-q", "100", inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.cwd, "in.jpg"), path.join(state.output.absolute, `${state.input.name}.jpg`))(state, p, cb);
