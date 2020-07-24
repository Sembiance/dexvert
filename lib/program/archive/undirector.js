"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/System25/drxtract",
	gentooPackage : "app-arch/drxtract",
	gentooOverlay : "dexvert"
};

exports.bin = () => "undirector";
exports.args = state => (["pc", state.input.filePath, state.output.dirPath]);
