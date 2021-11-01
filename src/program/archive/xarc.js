"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://fileformats.archiveteam.org/wiki/ARC_(compression_format)#ARC_Plus"
};

exports.dos = () => "XARC.EXE";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => ([inPath, outPath]);
