"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://www.irfanview.com/"
};

exports.qemu = () => "c:\\Program Files\\IrfanView\\i_view32.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "/silent", `/convert="c:\\out\\${state.input.name}.png"`]);
exports.qemuData = (state, p, r) => ({osid : "winxp", inFilePaths : [r.args[0]]});
