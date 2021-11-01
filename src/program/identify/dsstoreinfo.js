"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/gehaxelt/Python-dsstore",
	gentooPackage : "app-arch/dsstoreinfo"
};

exports.bin = () => "dsstoreinfo";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.redirectOutput = state => path.join(state.output.absolute, `${state.input.name}.txt`);
