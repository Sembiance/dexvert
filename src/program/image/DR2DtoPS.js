"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://aminet.net/package/docs/misc/dr2d.lha",
	unsafe  : true
};

exports.qemu = () => "DR2DtoPS";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, ">HD:out/outfile.ps"]);
exports.qemuData = (state, p, r) => ({osid : "amigappc", inFilePaths : [r.args[0]]});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.ps"), path.join(state.output.absolute, `${state.input.name}.ps`))(state, p, cb);
