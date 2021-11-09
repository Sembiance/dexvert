/*
import {Program} from "../../Program.js";

export class totalCADConverterX extends Program
{
	website = "https://www.coolutils.com/TotalCADConverterX";
	flags = {"outputFileType":"Which format to transform into (\"svg\", \"pdf\", \"png\", etc). LOWERCASE. See sandbox/app/totalCADXManual.txt for list. Default is \"svg\""};
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website : "https://www.coolutils.com/TotalCADConverterX",
	flags   :
	{
		// WARNING! I tried to do PNG and it complained about missing bcrypt.dll which is a Vista only file
		// So raster output may require Vista or higher
		outputFileType : `Which format to transform into ("svg", "pdf", "png", etc). LOWERCASE. See sandbox/app/totalCADXManual.txt for list. Default is "svg"`
	}
};

exports.qemu = () => "c:\\Program Files\\CoolUtils\\TotalCADConverterX\\CADConverterX.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, `c:\\out\\outfile.${r.flags.outputFileType || "svg"}`, "-WithoutBorder"]);
exports.qemuData = (state, p, r) => ({osid : "winxp", inFilePaths : [r.args[0]]});
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
				if((r.flags.outputFileType || "svg")==="svg")
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
