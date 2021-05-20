"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.meta =
{
	website       : "https://github.com/fuzziqersoftware/resource_dasm",
	gentooPackage : "app-arch/resource-dasm",
	gentooOverlay : "dexvert"
};

exports.bin = () => "resource_dasm";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["--data-fork", inPath, outPath]);

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputfiles()
		{
			fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
		},
		function renameOutputFiles(outputFilePaths)
		{
			const inputFileBase = path.basename(r.args[1]);
			outputFilePaths.parallelForEach((outputFilePath, subcb) => fs.rename(outputFilePath, outputFilePath.replaceAll(`${inputFileBase}_`, ""), subcb), this);
		},
		cb
	);
};
