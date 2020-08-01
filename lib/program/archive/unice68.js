"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://sourceforge.net/projects/sc68/",
	gentooPackage : "app-arch/unice68",
	gentooOverlay : "dexvert"
};

exports.bin = () => "unice68";
exports.args = state => (["-d", state.input.filePath, path.join(state.output.dirPath, "outfile")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, state.input.base))(state, p, cb);
