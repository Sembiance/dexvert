"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://sourceware.org/binutils/",
	gentooPackage : "sys-devel/binutils"
};

exports.bin = () => "ar";
exports.args = (state, p, r, inPath=state.input.filePath) => (["xo", inPath]);
exports.cwd = state => state.output.absolute;
