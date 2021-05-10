"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "http://infozip.sourceforge.net/",
	gentooPackage  : "app-arch/unzip",
	gentooOverlay  : "dexvert",
	gentooUseFlags : "bzip2 natspec smith unicode",
	notes          : "The version in dexvert overlay includes additional support for USE_SMITH via an unreduce_full.c patch from ftp://ftp.info-zip.org/pub/infozip/src/unreduce_full.zip"
};

exports.bin = () => "unzip";

// By passing 'nopasswd' to -P it avoids the program hanging when an archive requires a password
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["-od", outPath, "-P", "nopasswd", inPath]);
