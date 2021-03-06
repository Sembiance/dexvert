"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://aminet.net/package/util/pack/xfdmaster"
};

exports.qemu = () => "xfdDecrunch";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "HD:out/outfile"]);
exports.qemuData = (state, p, r) => ({osid : "amigappc", inFilePaths : [r.args[0]]});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, state.input.name))(state, p, cb);
