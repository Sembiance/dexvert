"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://www.cpcwiki.eu/forum/applications/cpcxfs/"
};

exports.wine = () => "cpcxfs/cpcxfsw.exe";
exports.args = (state, p, inPath=state.input.filePath) => ([inPath, "-mg", "*.*"]);
exports.cwd = state => state.output.absolute;
