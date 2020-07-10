"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://aminet.net/package/util/pack/decrunchmania-mos",
	gentooPackage : "app-arch/decrmtool",
	gentooOverlay : "dexvert"
};

exports.bin = () => "decrmtool";
exports.args = state => ([state.input.filePath, path.join(state.output.dirPath, "outfile")]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, state.input.name))(state, p, cb);
