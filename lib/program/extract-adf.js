"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://github.com/mist64/extract-adf",
	gentooPackage  : "app-arch/extract-adf",
	gentooOverlay  : "dexvert"
};

exports.bin = () => "extract-adf";
exports.cwd = state => state.output.absolute;
exports.args = state => (["-a", state.input.filePath]);
