"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "http://arc.sourceforge.net",
	gentooPackage : "app-arch/arc",
	bruteUnsafe   : true
};

exports.bin = () => "arc";
exports.args = (state, p, r, inPath=state.input.filePath) => (["x", inPath]);
exports.cwd = state => state.output.absolute;
