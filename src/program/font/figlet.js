"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "http://www.figlet.org/",
	gentooPackage : "app-misc/figlet"
};

exports.bin = () => "figlet";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-f", inPath, `abcdefghijklmnopqrstuvwxyz\nABCDEFGHIJKLMNOPQRSTUVWXYZ\n0123456789\n\`~!@#$%^&*()-_+=>;,<;.[]{}|\\:;"'/?`]);
exports.redirectOutput = state => path.join(state.output.absolute, `${state.input.name}.txt`);
