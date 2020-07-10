"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://entropymine.com/deark/",
	gentooPackage : "app-arch/deark",
	gentooOverlay : "dexvert"
};

exports.bin = () => "deark";
exports.args = state => (["-od", state.output.dirPath, "-o", state.input.name, state.input.filePath]);
