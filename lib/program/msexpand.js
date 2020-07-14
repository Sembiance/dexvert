"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://gnuwin32.sourceforge.net/packages/mscompress.htm",
	gentooPackage : "app-arch/mscompress"
};

exports.bin = () => "msexpand";
exports.args = state => ([state.input.filePath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.cwd, "in"), path.join(state.output.absolute, path.basename(state.input.base, (p.format.meta.ext || ["_"])[0])))(state, p, cb);
