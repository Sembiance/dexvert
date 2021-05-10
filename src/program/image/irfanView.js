"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://www.irfanview.com/",
	unsafe  : true
};

exports.qemu = () => "c:\\Program Files\\IrfanView\\i_view32.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "/silent", `/convert="c:\\out\\${state.input.name}.png"`]);
exports.qemuData = (state, p, r) => ({osid : "winxp", inFilePaths : [r.args[0]], timeout : XU.MINUTE});	// If it doesn't convert in 1 minute, it's not gonna as irfanview often gets stuck in infinite loops with max cpu usage
