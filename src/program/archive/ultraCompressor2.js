"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://files.mpoli.fi/unpacked/software/dos/compress/quant097.zip/"
};

exports.dos = () => "ULTRACMP/UC.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([`..\\${inPath.toUpperCase()}`]);
exports.dosData = (state, p, r) => ({includeDir : true, autoExec : ["CD OUT", `..\\ULTRACMP\\UC.EXE ES ${r.args}`]});
