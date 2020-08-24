"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://github.com/mist64/extract-adf",
	gentooPackage  : "app-arch/extract-adf",
	gentooOverlay  : "dexvert"
};

exports.bin = () => "extract-adf";
exports.args = (state, p, inPath=state.input.filePath) => (["-a", inPath]);
exports.cwd = state => state.output.absolute;
