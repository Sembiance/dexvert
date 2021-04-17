"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website : "https://wiki.amigaos.net/wiki/AmigaOS_Manual:_AmigaDOS_Command_Reference#COPY",
	slow    : true
};

exports.amiga = () => "copy";
exports.args =  (state, p, r, inPath=path.join(state.cwd, state.input.filePath)) => { r.floppyFilePath = inPath; return ["DF0:", "to", `"out:\`WHICH DF0:\`"`, "ALL", "CLONE", "QUIET"]; };
exports.amigaData = (state, p, r) => ({timeout : XU.MINUTE*2, floppyFilePaths : [r.floppyFilePath]});

exports.post = (state, p, r, cb) =>
{
	// The dexScript above creates a folder with the volume label in it, but with a semicolon at the end. Need to find that and remove it
	tiptoe(
		function findPRGOutputFiles()
		{
			fileUtil.glob(state.output.absolute, "*:/", this);
		},
		function stripPRGExtension(volDirPaths)
		{
			volDirPaths.parallelForEach((volDirPath, subcb) => fs.rename(volDirPath, volDirPath.slice(0, -1), subcb), this);
		},
		cb
	);
};
