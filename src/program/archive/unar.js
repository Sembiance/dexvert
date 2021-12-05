/*
import {Program} from "../../Program.js";

export class unar extends Program
{
	website = "https://unarchiver.c3.cx/";
	package = "app-arch/unar";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website       : "https://unarchiver.c3.cx/",
	package : "app-arch/unar"
};

exports.bin = () => "unar";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["-f", "-D", "-o", outPath, inPath]);

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputfiles()
		{
			fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
		},
		function renameOutputFiles(outputFilePaths)
		{
			if(outputFilePaths.length!==1)
				return this();
			
			const outputFilePath = outputFilePaths[0];
			fs.rename(outputFilePath, path.join(path.dirname(outputFilePath), state.input.name + path.extname(outputFilePath)), this);
		},
		cb
	);
};
*/
