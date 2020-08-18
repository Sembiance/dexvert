"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://gitlab.com/federicomenaquintero/bzip2",
	gentooPackage  : "app-arch/bzip2",
	gentooUseFlags : "split-usr"
};

exports.bin = () => "bunzip2";
exports.args = state => (["--force", state.input.filePath]);
exports.post = (state, p, cb) => p.util.file.move(path.join(state.cwd, "in"), path.join(state.output.absolute, state.input.name))(state, p, cb);
