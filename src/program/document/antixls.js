"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://packages.gentoo.org/packages/app-text/antixls",
	gentooPackage : "app-text/antixls"
};

exports.bin = () => "antixls";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.runOptions = state => ({"redirect-stdout" : path.join(state.output.absolute, `${state.input.name}.txt`)});
