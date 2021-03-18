"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website     : "https://www.isobuster.com/isobuster.php",
	bruteUnsafe : true	// Takes too long
};

exports.wine = () => "IsoBuster/IsoBuster.exe";
exports.wineOptions = () => ({
	isolate : true,	// Required due to IsoBuster having some sort of shared state that prevents multiple instances on the same wineserver
	timeout : XU.MINUTE*5
});

// IsoBuster command line options: https://www.isobuster.com/help/use_of_command_line_parameters
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => ([`/ef:${p.util.wine.path(outPath)}`, inPath.replaceAll("/", "\\"), "/c"]);
