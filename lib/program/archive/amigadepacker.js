"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://zakalwe.fi/~shd/foss/amigadepacker/",
	gentooPackage : "app-arch/amigadepacker",
	gentooOverlay : "dexvert"
};

exports.bin = () => "amigadepacker";
exports.args = state => (["-o", path.join(state.output.dirPath, "outfile"), state.input.filePath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, state.input.name))(state, p, cb);
