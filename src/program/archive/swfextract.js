/*
import {Program} from "../../Program.js";

export class swfextract extends Program
{
	website = "http://www.swftools.org/";
	package = "media-gfx/swftools";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	tiptoe = require("tiptoe");

exports.meta =
{
	website       : "http://www.swftools.org/",
	package : "media-gfx/swftools",
};

exports.bin = () => "swfextract";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["--outputformat", `${outPath}/%06d.%s`, "-a", "1-", inPath]);

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputFiles()
		{
			fileUtil.glob(state.output.absolute, "**", {nodir : true}, this);
		},
		function deleteBadFiles(filePaths)
		{
			filePaths.parallelForEach((filePath, subcb) =>
			{
				if(fs.statSync(filePath).size<=1)
					fileUtil.unlink(filePath, subcb);
				else
					setImmediate(subcb);
			}, this);
		},
		cb
	);
};
*/
