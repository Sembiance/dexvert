/*
import {Program} from "../../Program.js";

export class resource_dasm extends Program
{
	website = "https://github.com/fuzziqersoftware/resource_dasm";
	package = "app-arch/resource-dasm";
	flags = {"copyOriginalOnFail":"If resource_dasm fails to produce an output file, copy the original file over"};
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.meta =
{
	website       : "https://github.com/fuzziqersoftware/resource_dasm",
	package : "app-arch/resource-dasm",
	flags :
	{
		copyOriginalOnFail : "If resource_dasm fails to produce an output file, copy the original file over"
	}
};

exports.bin = () => "resource_dasm";
exports.preArgs = (state, p, r, cb) =>	// ROB DENO: preArgs stuff can now just be done inside of args itself, since it's async now
{
	r.tmpDirPath = fileUtil.generateTempFilePath(state.cwd);
	fs.mkdir(r.tmpDirPath, cb);
};
exports.args = (state, p, r, inPath=state.input.filePath) => (["--data-fork", inPath, r.tmpDirPath]);

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputfiles()
		{
			fileUtil.glob(r.tmpDirPath, "*", {nodir : true}, this);
		},
		function renameOutputFiles(outputFilePaths)
		{
			XU.log`outputFilePaths ${outputFilePaths} ${r.flags.copyOriginalOnFail}`;
			if(outputFilePaths.length===0)
			{
				if(r.flags.copyOriginalOnFail)
					fs.copyFile(r.args[1], path.join(state.output.absolute, path.basename(r.args[1])), this);
				else
					this();
				
				return;
			}

			const inputFileBase = path.basename(r.args[1]);
			outputFilePaths.parallelForEach((outputFilePath, subcb) => fs.rename(outputFilePath, path.join(state.output.absolute, path.basename(outputFilePath.replaceAll(`${inputFileBase}_`, ""))), subcb), this);
		},
		cb
	);
};
*/
