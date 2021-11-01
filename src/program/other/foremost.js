"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website       : "http://foremost.sourceforge.net/",
	gentooPackage : "app-forensics/foremost"
};

exports.bin = () => "foremost";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => ([`-o${outPath}`, inPath]);
exports.post = (state, p, r, cb) => fileUtil.unlink(path.join(state.output.absolute, "audit.txt"), cb);
