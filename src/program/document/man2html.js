"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website       : "http://primates.ximian.com/~flucifredi/man/",
	gentooPackage : "sys-apps/man2html"
};

exports.bin = () => "man2html";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.redirectOutput = state => path.join(state.output.absolute, `${state.input.name}.html`);
exports.post = (state, p, r, cb) =>
{
	const outputFilePath = path.join(state.output.absolute, `${state.input.name}.html`);
	if(fs.readFileSync(outputFilePath, XU.UTF8).includes("<H1>Invalid Manpage</H1>"))
		return fileUtil.unlink(outputFilePath, cb);

	fileUtil.searchReplace(outputFilePath, "Content-type: text/html", "", cb);
};
