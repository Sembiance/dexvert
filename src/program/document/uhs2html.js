"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://www.emulinks.de/software.html",
	gentooPackage : "games-util/uhs2html",
	unsafe        : true
};

exports.bin = () => "uhs2html";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "outhtml"]);
exports.post = (state, p, r, cb) => p.util.file.moveAllFiles(path.join(state.cwd, "outhtml"), state.output.absolute)(state, p, cb);
