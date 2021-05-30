"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	hashUtil = require("@sembiance/xutil").hash,
	fs = require("fs"),
	path = require("path"),
	tiptoe = require("tiptoe");

exports.meta =
{
	website       : "https://entropymine.com/deark/",
	gentooPackage : "app-arch/deark",
	gentooOverlay : "dexvert",
	flags :
	{
		dearkModule     : "Which deark module to forcibly set. Default: Let deark decide",
		dearkOpts       : "An array of additional -opt <option> arguments to pass to deark",
		dearkCharOutput : `Which type of output to use when converting character based files. Can be "image" or "html" Default: Let deark decide.`,
		dearkRemoveDups : "Remove any duplicate output files, based on sum. Default: false",
		dearkJoinFrames : "Treat output files as individual images frames of an animation and join them together as an MP4",
		dearkGIFDelay   : "Duration of delay between animation frames. Default: 12",
		dearkReplaceExt : "An object of keys that are extensions to replace with their values. Only works with a single output file.",
		keepAsGIF       : "If dearkJoinFrames is set, leave the animation as a GIF, don't convert to MP4"
	}
};

exports.BSAVE_TYPES = ["cga2", "cga4", "cga16", "mcga", "wh2", "wh4", "wh16", "b256", "2col", "4col"];		// "char" is also one, which produces an HTML file which we can't tensor verify, but haven't encountered a file that uses it yet, so we omit it

exports.bin = () => "deark";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath, outName=state.input.name) =>
{
	const args = [];
	if(r.flags.dearkModule)
		args.push("-m", r.flags.dearkModule);
	const opts = Array.from(r.flags.dearkOpts || []);
	if(r.flags.dearkCharOutput)
		opts.push(`char:output=${r.flags.dearkCharOutput || "image"}`);
		
	return [...args, ...opts.flatMap(opt => (["-opt", opt])), "-od", outPath, "-o", outName, inPath];
};

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
			function getSums(outputFilePaths)
			{
				this.data.outputFilePaths = outputFilePaths;
				if(r.flags.dearkRemoveDups)
					this.data.outputFilePaths.parallelForEach((outputFilePath, subcb) => hashUtil.hashFile("blake3", outputFilePath, subcb), this);
				else
					this();
			},
			function convertOutputFiles(hashSums)
			{
				this.data.outputFilePathsToRemove = [];
				const seenSums = [];

				this.data.outputFilePaths.parallelForEach((outputFilePath, subcb, i) =>
				{
					if(r.flags.dearkRemoveDups)
					{
						// Deark often generates a lot of identical files for image conversion. Delete duplicate files if instructed
						const hashSum = hashSums[i];
						if(!seenSums.includes(hashSum))
							seenSums.push(hashSum);
						else
							this.data.outputFilePathsToRemove.pushUnique(outputFilePath);
					}

					const ext = path.extname(outputFilePath);
					if(![".jp2", ".bmp", ".tif", ".tiff", ".qtif", ".pgc"].includes(ext))
						return setImmediate(subcb);

					this.data.outputFilePathsToRemove.pushUnique(outputFilePath);

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
				// If we have only 1 file, remove any useless prefixes/suffixes
				if(outputFilePaths.length===1)
				{
					let newOutputFilename = path.basename(outputFilePaths[0]);

					const dropExts = [".000", ...exports.BSAVE_TYPES.map(v => `_${v}`)].filter(v => newOutputFilename.includes(v));
					if(dropExts.length>0)
						dropExts.forEach(dropExt => { newOutputFilename = newOutputFilename.replaceAll(dropExt, ""); });

					Object.forEach((r.flags.dearkReplaceExt || {}), (fromExt, toExt) => { newOutputFilename = newOutputFilename.replaceAll(fromExt, toExt); });

					if(newOutputFilename!==path.basename(outputFilePaths[0]))
						fs.rename(outputFilePaths[0], path.join(path.dirname(outputFilePaths[0]), newOutputFilename), this.finish);
					else
						this.finish();
					
					return;
				}

				// Deark prefixes every file it extracts from an archive with an ascending order NAME.###.
				// Let's check to see if it's safe to remove all these prefixes, so long as the resulting renames wouldn't cause file name collisions
				const beforeFilePaths = outputFilePaths.map(outputFilePath => path.relative(state.output.absolute, outputFilePath));
				const seenShortPaths = {};
				const afterFilePaths = beforeFilePaths.map(beforeFilePath =>
				{
					// Only proceed if it starts with FILENAME.###.
					if(!beforeFilePath.startsWith(state.input.name) || !(/^\.\d{3}\./).test(beforeFilePath.substring(state.input.name.length)))
						return beforeFilePath;
					
					let shortFilePath = beforeFilePath.substring(state.input.name.length + 5);
					
					// Only proceed if the resulting file has a period in it or is > 3 characters long (to prevent ending up with just 'png' as a resulting filename)
					if(!shortFilePath.includes(".") && shortFilePath.length<=3)
						return beforeFilePath;
					
					if(seenShortPaths.hasOwnProperty(shortFilePath))
						shortFilePath = `${path.basename(shortFilePath, path.extname(shortFilePath))}_${(++seenShortPaths[shortFilePath]).toString().padStart(3, "0")}${path.extname(shortFilePath)}`;
					else
						seenShortPaths[shortFilePath] = 0;

					//XU.log`deark renaming: ${beforeFilePath} => ${shortFilePath}`;

					return shortFilePath;
				});

				if(beforeFilePaths.subtractAll(afterFilePaths)===0 || afterFilePaths.slice().unique().length!==afterFilePaths.length)
					return this.finish();

				this.data.outputFilePaths = outputFilePaths;
				if(typeof r.flags.dearkJoinFrames==="function")
					r.flags.dearkJoinFrames = r.flags.dearkJoinFrames(state, p, r, outputFilePaths);

				if(r.flags.dearkJoinFrames)
				{
					this.data.GIFFilePath = path.join(state.output.absolute, `${state.input.name}.gif`);
					p.util.program.run("convert", {args : ["-delay", `${r.flags.dearkGIFDelay || 12}`, "-loop", "0", "-dispose", "previous", ...outputFilePaths, ...p.util.program.args(state, p, "convert").slice(1, -1), this.data.GIFFilePath]})(state, p, this);
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
				
				(this.data.outputFilePaths || []).parallelForEach((outputFilePath, subcb) => fileUtil.unlink(outputFilePath, subcb), this);
			},
			function convertToMP4()
			{
				if(r.flags.keepAsGIF)
					return this.finish();

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
