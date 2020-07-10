"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "http://www.svgalib.org/rus/lbrate.html",
	gentooPackage : "app-arch/lbrate",
	gentooOverlay : "dexvert"
};

exports.bin = () => "lbrate";
exports.cwd = state => state.output.absolute;
exports.args = state => ([state.input.filePath]);
