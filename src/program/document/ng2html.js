"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "http://www.davep.org/norton-guides/",
	gentooPackage : "app-text/ng2html",
	gentooOverlay : "dexvert",
	unsafe        : true
};

exports.bin = () => "ng2html";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.cwd = state => state.output.absolute;
