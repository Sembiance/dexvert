"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "http://www.ctpax-x.org/?goto=files&show=104",
	gentooPackage : "app-arch/unpcx",
	gentooOverlay : "dexvert"
};

exports.bin = () => "unpcx";
exports.args = state => ([state.input.filePath, state.output.dirPath]);
