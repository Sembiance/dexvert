"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://unarchiver.c3.cx/",
	gentooPackage  : "app-arch/unar"
};

exports.bin = () => "unar";
exports.args = state => (["-f", "-D", "-o", state.output.dirPath, state.input.filePath]);
