"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : ["https://github.com/System25/drxtract", "https://www.python.org/"],
	gentooPackage : ["app-arch/drxtract", "=dev-lang/python-2*"],
	gentooOverlay : ["dexvert", "gentoo"],
	bin           : ["*", "python2.7"]
};

exports.bin = () => "undirector";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["pc", inPath, outPath]);
