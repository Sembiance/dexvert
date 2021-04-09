"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website     : "https://www.isobuster.com/isobuster.php",
	bruteUnsafe : true	// Takes too long
};

exports.qemu = () => "c:\\Program Files\\Smart Projects\\IsoBuster\\IsoBuster.exe";

// IsoBuster command line options: https://www.isobuster.com/help/use_of_command_line_parameters
exports.args = (state, p, r, inPath=state.input.filePath) => (["/ef:all:C:\\out", inPath, "/c"]);

exports.qemuData = (state, p, r) => ({osid : "winxp", inFilePaths : [r.args[1], ...(state.extraFilenames || [])]});
