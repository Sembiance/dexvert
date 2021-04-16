"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://www.speedproject.com/download/old/"
};

exports.qemu = () => "c:\\Program Files\\SpeedProject\\Squeez 5\\sqc.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => (["x", inPath]);
exports.qemuData = (state, p, r) => ({cwd : "c:\\out", inFilePaths : [r.args.last()]});
