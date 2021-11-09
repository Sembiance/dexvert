/*
import {Program} from "../../Program.js";

export class drawview extends Program
{
	website = "http://www.keelhaul.me.uk/acorn/drawview/";
	gentooPackage = "media-gfx/drawview";
	gentooOverlay = "dexvert";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website       : "http://www.keelhaul.me.uk/acorn/drawview/",
	gentooPackage : "media-gfx/drawview",
	gentooOverlay : "dexvert"
};

exports.bin = () => "drawview";
exports.runOptions = () => ({virtualX : true});
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath)) => (["-e", outPath, inPath]);

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
				const finalOutputFilePath = path.join(path.dirname(outputFilePath), path.basename(outputFilePath).replaceAll(path.basename(r.args.last(), path.extname(r.args.last())), state.input.name));
				tiptoe(
					function removeDynamicTags()
					{
						p.util.program.run("deDynamicSVG", {argsd : [outputFilePath, finalOutputFilePath]})(state, p, this);
					},
					function cropSVG()
					{
						// The SVGs from acorn are often horribly cropped wrong and cut off, this will fix that
						runUtil.run("inkscape", ["-g", "--batch-process", "--verb", "FitCanvasToDrawing;FileSave;FileClose", finalOutputFilePath], {silent : !state.verbose, virtualX : true}, this);
					},
					subcb
				);
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
