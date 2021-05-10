"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://packages.debian.org/jessie/zoo",
	gentooPackage : "app-arch/zoo"
};

exports.bin = () => "zoo";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-extract", inPath]);
exports.cwd = state => state.output.absolute;
