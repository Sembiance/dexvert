"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	tiptoe = require("tiptoe");

exports.meta =
{
	website       : "https://entropymine.com/deark/",
	gentooPackage : "app-arch/deark",
	gentooOverlay : "dexvert"
};

exports.bin = () => "deark";
exports.args = state => (["-od", state.output.dirPath, "-o", state.input.name, state.input.filePath]);
exports.post = (state, p, cb) =>
{
	// Deark's newprintshop module can convert almost any file into a bunch of garbage
	if(!state.id.brute || !state.run.deark[0].startsWith("Module: newprintshop"))
		return setImmediate(cb);
	
	tiptoe(
		function removeOutputDir()
		{
			fileUtil.unlink(state.output.absolute, this);
		},
		function recreateOutputDir()
		{
			fs.mkdir(state.output.absolute, this);
		},
		cb
	);
};
