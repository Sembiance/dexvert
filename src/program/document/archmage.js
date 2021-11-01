"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/dottedmag/archmage",
	gentooPackage : "app-text/archmage",
	notes         : "Right now we just extract all the files, raw. archmage says it can convert to better HTML or PDF but it's got bugs and that doesn't work."
};

exports.bin = () => "archmage";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-x", inPath, "outfiles"]);
exports.post = (state, p, r, cb) => p.util.file.moveAllFiles(path.join(state.cwd, "outfiles"), state.output.absolute)(state, p, cb);
