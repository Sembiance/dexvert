"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://archive.org/details/msdos_festival_PUT345",
	unsafe  : true
};

exports.dos = () => "GET.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.dosData = (state, p, r) => ({timeout : XU.MINUTE, autoExec : [`GET.EXE ${r.args[0]} E:\\OUT QUIET`]});
