"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website     : "https://www.isobuster.com/isobuster.php",
	bruteUnsafe : true	// Takes too long
};

exports.wine = () => "IsoBuster/IsoBuster.exe";
exports.wineOptions = () => ({timeout : XU.MINUTE*10});

// IsoBuster command line options: https://www.isobuster.com/help/use_of_command_line_parameters
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => ([`/ef:${p.util.wine.path(outPath)}`, inPath.replaceAll("/", "\\"), "/c"]);
