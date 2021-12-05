/*
import {Program} from "../../Program.js";

export class asapconv extends Program
{
	website = "http://asap.sourceforge.net/";
	package = "media-sound/asap";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	path = require("path");

exports.meta =
{
	website        : "http://asap.sourceforge.net/",
	package  : "media-sound/asap",
};

exports.bin = () => "asapconv";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile%s.wav")) => (["-o", outPath, inPath]);

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputfiles()
		{
			fileUtil.glob(state.output.absolute, "*.wav", {nodir : true}, this);
		},
		function renameFiles(outputFilePaths)
		{
			if(outputFilePaths.length===1)
				fs.rename(outputFilePaths[0], path.join(state.output.absolute, `${state.input.name}.wav`), this);
			else
				outputFilePaths.parallelForEach((outputFilePath, subcb) => fs.rename(outputFilePath, path.join(path.dirname(outputFilePath), path.basename(outputFilePath).replaceAll("outfile", state.input.name)), subcb), this);
		},
		cb
	);
};
*/
