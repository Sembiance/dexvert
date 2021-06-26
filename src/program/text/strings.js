"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://www.gnu.org/software/binutils/",
	gentooPackage : "sys-devel/binutils"
};

exports.bin = () => "strings";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-a", inPath]);
exports.redirectOutput = state => path.join(state.output.absolute, `${state.input.name}.txt`);
