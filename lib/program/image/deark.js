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
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath, outName=state.input.name) => (["-opt", `char:output=${r.flags.dearkCharOutput || "image"}`, "-od", outPath, "-o", outName, inPath]);

exports.post = (state, p, r, cb) =>
{
	if(state.id.brute && (r.results || "").trim().startsWith("Module: newprintshop"))
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
		tiptoe(
			function findOutputfiles()
			{
				// Deark sometimes creates BMP/JP2/TIFF files instead of PNG files. Let's find them and convert them to PNG
				fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
			},
			function convertOutputFiles(outputFilePaths)
			{
				this.data.outputFilePathsToRemove = [];

				outputFilePaths.parallelForEach((outputFilePath, subcb) =>
				{
					const ext = path.extname(outputFilePath);
					if(![".jp2", ".bmp", ".tif", ".tiff", ".qtif", ".pgc"].includes(ext))
						return setImmediate(subcb);

					this.data.outputFilePathsToRemove.push(outputFilePath);

					if(ext===".qtif")
						p.util.program.run("abydosconvert", {args : ["image/qtif", path.join(state.output.dirPath, path.basename(outputFilePath)), state.output.dirPath]})(state, p, subcb);
					else if(ext===".pgc")
						p.util.program.run("recoil2png", {argsd : [path.join(state.output.dirPath, path.basename(outputFilePath)), path.join(state.output.absolute, `${path.basename(outputFilePath, ext)}.png`)]})(state, p, subcb);
					else
						p.util.program.run("convert", {argsd : [path.join(state.output.dirPath, path.basename(outputFilePath)), path.join(state.output.dirPath, `${path.basename(outputFilePath, ext)}.png`)]})(state, p, subcb);
				}, this);
			},
			function removeBadOutputFiles()
			{
				this.data.outputFilePathsToRemove.parallelForEach(fileUtil.unlink, this);
			},
			function findOutputFilesAgain()
			{
				fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
			},
			function renameIfNeeded(outputFilePaths)
			{
				// If we have only 1 file, remove any useless .000. prefix/suffix
				if(outputFilePaths.length===1)
				{
					if(!outputFilePaths[0].includes(".000."))
						return this.finish();
					
					fs.rename(outputFilePaths[0], path.join(path.dirname(outputFilePaths[0]), path.basename(outputFilePaths[0]).replaceAll(".000.", ".")), this);
					return;
				}

				// Deark prefixes every file it extracts from an archive with an ascending order NAME.###.
				// Let's check to see if it's safe to remove all these prefixes, so long as the resulting renames wouldn't cause file name collisions
				const beforeFilePaths = outputFilePaths.map(outputFilePath => path.relative(state.output.absolute, outputFilePath));
				const afterFilePaths = beforeFilePaths.map(beforeFilePath =>
				{
					// Only proceed if it starts with FILENAME.###.
					if(!beforeFilePath.startsWith(state.input.name) || !beforeFilePath.substring(state.input.name.length).match(/^\.\d{3}\./))
						return beforeFilePath;
					
					const shortFilePath = beforeFilePath.substring(state.input.name.length + 5);
					
					// Only proceed if the resulting file has a period in it or is > 3 characters long (to prevent ending up with just 'png' as a resulting filename)
					if(!shortFilePath.includes(".") && shortFilePath.length<=3)
						return beforeFilePath;
					
					return shortFilePath;
				});
				if(beforeFilePaths.subtractAll(afterFilePaths)===0 || afterFilePaths.slice().unique().length!==afterFilePaths.length)
					return this.finish();

				this.data.outputFilePaths = outputFilePaths;

				if(r.flags.dearkJoinFrames)
				{
					this.data.GIFFilePath = path.join(state.output.absolute, `${state.input.name}.gif`);
					p.util.program.run("convert", {args : ["-delay", "12", "-loop", "0", "-dispose", "previous", ...outputFilePaths, ...p.util.program.args(state, p, "convert").slice(1, -1), this.data.GIFFilePath]})(state, p, this);
				}
				else
				{
					outputFilePaths.parallelForEach((outputFilePath, subcb, i) => fs.rename(outputFilePath, path.join(state.output.absolute, afterFilePaths[i]), subcb), this);
				}
			},
			function deleteFramesIfNeeded()
			{
				if(!r.flags.dearkJoinFrames)
					return this.finish();
				
				this.data.outputFilePaths.parallelForEach((outputFilePath, subcb) => fileUtil.unlink(outputFilePath, subcb), this);
			},
			function convertToMP4()
			{
				p.util.program.run("ffmpeg", {flags : {ffmpegExt : ".mp4"}, argsd : [this.data.GIFFilePath]})(state, p, this);
			},
			function removeSourceGIF()
			{
				fileUtil.unlink(this.data.GIFFilePath, this);
			},
			cb
		);
	}
};
