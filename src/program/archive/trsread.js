"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://www.trs-80emulators.com/trsread-trswrite.html"
};

exports.qemu = () => "trsread.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-e", "-s", "-i", inPath]);
exports.qemuData = (state, p, r) => ({osid : "winxp", cwd : "c:\\out", inFilePaths : [r.args.last()]});
