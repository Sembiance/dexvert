"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://aminet.net/package/dev/misc/ab2ascii-1.3",
	gentooPackage : "dev-lang/ab2ascii",
	gentooOverlay : "dexvert"
};

exports.bin = () => "ab2ascii";
exports.args = state => (["-o", path.join(state.output.dirPath, "outfile.txt"), state.input.filePath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.txt"), path.join(state.output.absolute, `${state.input.name}_amigaBASIC.txt`))(state, p, cb);
