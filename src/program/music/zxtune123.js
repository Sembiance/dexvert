/*
import {Program} from "../../Program.js";

export class zxtune123 extends Program
{
	website = "https://zxtune.bitbucket.io/";
	gentooPackage = "media-sound/zxtune";
	gentooOverlay = "dexvert";
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
	website       : "https://zxtune.bitbucket.io/",
	gentooPackage : "media-sound/zxtune",
	gentooOverlay : "dexvert"
};

exports.bin = () => "zxtune123";
exports.args = (state, p, r, inPath=state.input.filePath) => (["--file", inPath, `--wav=filename=${state.output.dirPath}/[Fullpath].wav`]);

// Some file types like NSF can have multiple sub-tunes so we have to supply a [Fullpath] template to zxtune which now we have to rename the files back to the proper names below
exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputfiles()
		{
			fileUtil.glob(state.output.absolute, "*.wav", {nodir : true}, this);
		},
		function renameFiles(outputFilePaths)
		{
			outputFilePaths.parallelForEach((outputFilePath, subcb) =>
			{
				let newFilename = path.basename(outputFilePath).replaceAll(path.basename(r.args[1]), state.input.name);
				const songNum = newFilename.match(/_#(?<songNum>\d+)/)?.groups?.songNum;
				if(songNum)
					newFilename = newFilename.replaceAll(`_#${songNum}`, `_${songNum.padStart(3, "0")}`);
				
				fs.rename(outputFilePath, path.join(path.dirname(outputFilePath), newFilename), subcb);
			}, this);
		},
		cb
	);
};
*/
