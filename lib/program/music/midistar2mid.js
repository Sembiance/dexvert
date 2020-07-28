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
exports.args = state => ([state.input.filePath, path.join(state.output.dirPath, "outfile.mid")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.mid"), path.join(state.output.absolute, `${state.input.name}.mid`))(state, p, cb);
