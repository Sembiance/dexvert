import {Program} from "../../Program.js";

export class deark extends Program
{
	website       = "https://entropymine.com/deark/";
	gentooPackage = "app-arch/deark";
	gentooOverlay = "dexvert";

	flags =
	{
		"module"      : "Which deark module to forcibly set. For list run `deark -modules` Default: Let deark decide",
		"charOutType" : "Which type of output to use when converting character based files. Can be \"image\" or \"html\" Default: Let deark decide.",
		"opts"        : "An array of additional -opt <option> arguments to pass to deark. For list see: https://github.com/jsummers/deark",
		"noThumbs"    : "Don't extract any thumb files found",
		"file2"       : "An extra file that can be used by deark module to get the correct palette or image names"
		//"dearkGIFDelay"   : "Duration of delay between animation frames. Default: 12",
		//"dearkJoinFrames" : "Treat output files as individual images frames of an animation and join them together as an MP4",
		//"dearkKeepAsGIF"  : "If dearkJoinFrames is set, leave the animation as a GIF, don't convert to MP4",
		//"dearkRemoveDups" : "Remove any duplicate output files, based on sum. Default: false",
		//"dearkReplaceExt" : "An object of keys that are extensions to replace with their values. Only works with a single output file."};
	};

	bin  = "deark";
	outExt = ".png";
	args = r =>
	{
		const a = ["-maxfiles", "9999"];
		if(r.flags.module)
			a.push("-m", r.flags.module);
		if(r.flags.noThumbs)
			a.push("-main");
		if(r.flags.file2)
			a.push("-file2", r.flags.file2);
		
		const opts = Array.force(r.flags.opts || []);
		if(r.flags.charOutType)
			opts.push(`char:output=${r.flags.charOutType || "image"}`);
		
		return [...a, ...opts.flatMap(opt => (["-opt", opt])), "-od", r.outDir(), "-o", "out", r.inFile()];
	};
	// deark output names can be useful such as image/macPaint/test.mac becoming out.000.Christie Brinkley.png which we want to turn into Christie Brinkley.png
	renameOut = {regex : /^.+(?<num>\.\d{3})(?<post>\..+)$/};

	verify = r =>
	{
		// Deark's newprintshop module can convert almost any file into a bunch of garbage. So if that was used, nothing from it is worth keeping
		if(r.stdout.includes("Module: newprintshop"))
			return false;

		return true;
	}
}

/*
exports.meta =
{
	flags :
	{
		dearkGIFDelay   : "Duration of delay between animation frames. Default: 12",
		dearkJoinFrames : "Treat output files as individual images frames of an animation and join them together as an MP4",
		dearkKeepAsGIF  : "If dearkJoinFrames is set, leave the animation as a GIF, don't convert to MP4",
		dearkModule     : "Which deark module to forcibly set. For list run `deark -modules` Default: Let deark decide",
		dearkOpts       : "An array of additional -opt <option> arguments to pass to deark. For list see: https://github.com/jsummers/deark",
		dearkRemoveDups : "Remove any duplicate output files, based on sum. Default: false",
		dearkReplaceExt : "An object of keys that are extensions to replace with their values. Only works with a single output file."
	}
};

// DEARK FORMATS: https://github.com/jsummers/deark/blob/master/formats.txt

exports.post = (state, p, r, cb) =>
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

				// If the file isn't a known image format, just return
				if(![".jp2", ".bmp", ".tif", ".tiff", ".qtif", ".pgc"].includes(ext))
					return setImmediate(subcb);

				// Otherwise we have an intermediatery format, so let's just convert it the rest of the way
				// We used to convert directly with nconvert/convert/etc but this loses our timestamps and doesn't allow fallback to other converters, so we run through dexvert instead
				p.util.program.run("dexvert", {argsd : [outputFilePath, state.output.absolute], flags : {deleteInput : true}})(state, p, subcb);
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
			if(r.flags.dearkKeepAsGIF)
				return this.finish();

			p.util.program.run("ffmpeg", {flags : {ffmpegExt : ".mp4"}, argsd : [this.data.GIFFilePath]})(state, p, this);
		},
		function removeSourceGIF()
		{
			fileUtil.unlink(this.data.GIFFilePath, this);
		},
		cb
	);
};
*/
