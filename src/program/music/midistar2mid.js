"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/midistar2mid",
	gentooPackage : "media-sound/midistar2mid",
	gentooOverlay : "dexvert"
};

exports.bin = () => "midistar2mid";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.mid")) => ([inPath, outPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.mid"), path.join(state.output.absolute, `${state.input.name}.mid`))(state, p, cb);
