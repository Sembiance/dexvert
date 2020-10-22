"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://sk1project.net/uc2/",
	gentooPackage : "media-gfx/uniconvertor",
	gentooOverlay : "dexvert"
};

exports.bin = () => "uniconvertor";

exports.args = (state, p, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.svg")) => ([inPath, outPath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.svg"), path.join(state.output.absolute, `${state.input.name}.svg`))(state, p, cb);
