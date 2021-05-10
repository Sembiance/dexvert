"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://www.gnu.org/software/tar/",
	gentooPackage  : "app-arch/tar",
	gentooUseFlags : "acl nls xattr"
};

exports.bin = () => "tar";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["-xf", inPath, "-C", outPath]);
