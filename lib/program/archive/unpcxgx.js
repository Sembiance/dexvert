"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://www.ctpax-x.org/?goto=files&show=104"
};

exports.qemu = () => "unpcxgx.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.qemuOptions = (state, p, r) => ({cwd : "c:\\out", inFilePaths : [r.args[0]]});
