"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://github.com/jca02266/lha",
	gentooPackage  : "app-arch/lha"
};

exports.bin = () => "lha";
exports.args = state => (["-x", "-w=" + state.output.dirPath, state.input.filePath]);
