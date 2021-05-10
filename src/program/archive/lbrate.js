"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "http://www.svgalib.org/rus/lbrate.html",
	gentooPackage : "app-arch/lbrate",
	gentooOverlay : "dexvert"
};

exports.bin = () => "lbrate";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.cwd = state => state.output.absolute;
