"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://www.gnu.org/software/gzip/",
	gentooPackage  : "app-arch/gzip"
};

exports.bin = () => "gunzip";
exports.args = (state, p, r, inPath=state.input.filePath) => (["--force", inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.cwd, "in"), path.join(state.output.absolute, state.input.name))(state, p, cb);
