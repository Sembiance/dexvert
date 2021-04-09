"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://www.reaconverter.com/"
};

exports.qemu = () => "c:\\Program Files\\reaConverter 7 Pro\\cons_rcp.exe";

// reaConverter command line help: https://www.reaconverter.com/howto/category/command-line-2/
exports.args = (state, p, r, inPath=state.input.filePath) => (["-s", inPath, "-o", `c:\\out\\${state.input.name}${(r.flags.reaConverterExt || ".png")}`]);

exports.qemuData = (state, p, r) => ({osid : "winxp", timeout : XU.MINUTE, inFilePaths : [r.args[1]]});


