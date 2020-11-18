"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website       : "https://github.com/dschwen/amosbank",
	gentooPackage : "dev-lang/amosbank",
	gentooOverlay : "dexvert"
};

exports.bin = () => "amosbank";
exports.cwd = state => state.output.absolute;

exports.pre = (state, p, r, cb) => fs.symlink(state.input.absolute, path.join(state.output.absolute, "in.abk"), cb);
exports.args = (state, p, r, inPath="in.abk") => ([inPath]);

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function removeTempFile()
		{
			fileUtil.unlink(path.join(state.output.absolute, "in.abk"), this);
		},
		function findOutputfiles()
		{
			fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
		},
		function renameOutputFiles(outputFilePaths)
		{
			outputFilePaths.parallelForEach((outputFilePath, subcb) => fs.rename(outputFilePath, outputFilePath.replaceAll("in.abk", state.input.name), subcb), this);
		},
		cb
	);
};
