"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/twogood/unshield",
	gentooPackage : "app-arch/unshield",
	flags :
	{
		unshieldUseOldCompression : "Set to true to instruct unshield to decompress using the old compression method. Default: false"
	}
};

exports.bin = () => "unshield";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => ([...(r.flags.unshieldUseOldCompression ? ["-O"] : []), "-d", outPath, "x", inPath]);