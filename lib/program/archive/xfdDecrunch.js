"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://aminet.net/package/util/pack/xfdmaster"
};

exports.amiga = () => "xfdDecrunch";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "out:outfile"]);
exports.amigaData = (state, p, r) => ({inFilePaths : [r.args[0]]});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, state.input.name))(state, p, cb);
