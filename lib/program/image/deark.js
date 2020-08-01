"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	path = require("path"),
	tiptoe = require("tiptoe");

exports.meta =
{
	website       : "https://entropymine.com/deark/",
	gentooPackage : "app-arch/deark",
	gentooOverlay : "dexvert"
};

exports.bin = () => "deark";
exports.args = state => (["-od", state.output.dirPath, "-o", state.input.name, state.input.filePath]);
exports.post = (state, p, cb) =>
{
	if(state.id.brute && state.run.deark[0].startsWith("Module: newprintshop"))
	{
		// Deark's newprintshop module can convert almost any file into a bunch of garbage
		tiptoe(
			function removeOutputDir()
			{
				fileUtil.unlink(state.output.absolute, this);
			},
			function recreateOutputDir()
			{
				fs.mkdir(state.output.absolute, this);
			},
			cb
		);
	}
	else
	{
		// Deark sometimes creates BMP or JP2 files instead of PNG files
		tiptoe(
			function findOutputfiles()
			{
				fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
			},
			function convertOutputFiles(outputFilePaths)
			{
				this.data.outputFilePathsToRemove = [];

				outputFilePaths.parallelForEach((outputFilePath, subcb) =>
				{
					const ext = path.extname(outputFilePath);
					if(![".jp2", ".bmp", ".tif", ".tiff", ".qtif"].includes(ext))
						return setImmediate(subcb);

					this.data.outputFilePathsToRemove.push(outputFilePath);

					if(ext===".qtif")
						p.util.program.run(p.program.abydosconvert, {args : ["image/qtif", path.join(state.output.dirPath, path.basename(outputFilePath)), state.output.dirPath]})(state, p, subcb);
					else
						p.util.program.run(p.program.convert, {args : [path.join(state.output.dirPath, path.basename(outputFilePath)), ...p.program.convert.STRIP_ARGS, path.join(state.output.dirPath, `${path.basename(outputFilePath, ext)}.png`)]})(state, p, subcb);
				}, this);
			},
			function removeBadOutputFiles()
			{
				this.data.outputFilePathsToRemove.parallelForEach(fileUtil.unlink, this);
			},
			cb
		);
	}
};
