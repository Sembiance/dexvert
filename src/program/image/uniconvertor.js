/*
import {Program} from "../../Program.js";

export class uniconvertor extends Program
{
	website = "https://sk1project.net/uc2/";
	gentooPackage = "media-gfx/uniconvertor";
	gentooOverlay = "dexvert";
	flags = {"uniconvertorExt":"Which extension to convert to (\".svg\", \".png\"). Default: .svg"};
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website       : "https://sk1project.net/uc2/",
	gentooPackage : "media-gfx/uniconvertor",
	gentooOverlay : "dexvert",
	flags         :
	{
		uniconvertorExt : `Which extension to convert to (".svg", ".png"). Default: .svg`
	}
};

exports.bin = () => "uniconvertor";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, `outfile${r.flags.uniconvertorExt || ".svg"}`)) => ([inPath, outPath]);
exports.runOptions = () => ({timeout : XU.MINUTE*3});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputfiles()
		{
			fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
		},
		function renameFiles(outputFilePaths)
		{
			this.data.outputFilePaths = outputFilePaths;

			outputFilePaths.parallelForEach((outputFilePath, subcb) =>
			{
				const finalOutputFilePath = path.join(path.dirname(outputFilePath), path.basename(outputFilePath).replaceAll("outfile", state.input.name));

				// SVG files produced by TotalCADConverter have a border, let's crop it by modifying our viewBox
				if((r.flags.uniconvertorExt || ".svg")===".svg")
					p.util.program.run("deDynamicSVG", {argsd : [outputFilePath, finalOutputFilePath]})(state, p, subcb);
				else
					fileUtil.move(outputFilePath, finalOutputFilePath, subcb);
			}, this);
		},
		function removeOriginals()
		{
			this.data.outputFilePaths.parallelForEach((outputFilePath, subcb) => p.util.file.unlink(outputFilePath)(state, p, subcb), this);
		},
		cb
	);
};
*/
