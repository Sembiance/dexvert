"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://www.ctpax-x.org/?goto=files&show=104"
};

exports.wine = () => "unpcxgx.exe";
exports.args = (state, p, inPath=state.input.filePath) => ([inPath]);
exports.cwd = state => state.output.absolute;
