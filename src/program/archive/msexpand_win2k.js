"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://www.computerhope.com/expandhl.htm",
	notes : "Warning: EXPAND.EXE will just 'copy' the source file over to the destination if it can't extract it."
};

exports.qemu = () => "c:\\WINNT\\system32\\expand.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "c:\\out\\"]);
exports.qemuData = (state, p, r) => ({inFilePaths : [r.args[0]]});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile"), path.join(state.output.absolute, `${state.input.name}${state.input.ext.trimChars("_")}`))(state, p, cb);
