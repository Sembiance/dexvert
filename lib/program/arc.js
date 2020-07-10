"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "http://arc.sourceforge.net",
	gentooPackage : "app-arch/arc"
};

exports.bin = () => "arc";
exports.cwd = state => state.output.absolute;
exports.args = state => (["x", state.input.filePath]);
