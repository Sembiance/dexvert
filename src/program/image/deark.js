import {xu} from "xu";
import {Program, RUNTIME, CONVERT_PNG_ARGS} from "../../Program.js";
import {encodeUtil, fileUtil, runUtil, imageUtil} from "xutil";
import {path} from "std";
import {quickConvertImages} from "../../dexUtil.js";

const BAD_FILENAMES_TO_SKIP_CHAINING =
[
	"binddll.dll"	// Has 43 BMP files which are actually just static (https://github.com/jsummers/deark/issues/55) which super slows everything thing down, so just skip it
];

function restRenamer(rest, suffix, newName)
{
	// if we don't have a period in our rest, then if it's a common extension fall back on our newName
	if(!rest.includes("."))
		return ["gif", "png", "ico", "jpg", "bmp", "eps", "svg", "jp2", "qtif", "tif", "tiff", "txt", "bin", "ptr", "icns", "wmf"].includes(rest) && newName ? [newName, suffix, ".", rest] : [suffix, rest];
	
	const restParts = rest.split(".");
	return [restParts.slice(0, -1).join("."), suffix, ".", restParts.at(-1)];
}

export class deark extends Program
{
	website = "https://entropymine.com/deark/";
	package = "app-arch/deark";
	flags   = {
		mac           : "Set this flag to treat the files extracted as mac files and rename them",
		module        : "Which deark module to forcibly set. For list run `deark -modules` Default: Let deark decide",
		charOutType   : "Which type of output to use when converting character based files. Can be \"image\" or \"html\" Default: Let deark decide.",
		opt           : "An array of additional -opt <option> arguments to pass to deark. For list see: https://github.com/jsummers/deark",
		noThumbs      : "Don't extract any thumb files found",
		recombine     : "Try to recombine multiple output images back into a single output image",
		onlyIfOne     : "Only 'succeed' if there is just a single output file",
		deleteADF     : "Set this to delete the output ADF file as it's not needed. This is mainly used when a simple image format like TIFF is wrapped as a MacBinary file.",
		convertAsExt  : "Use this ext as a hint as to what to convert as",
		alwaysConvert : "Always convert output files using convert[removeAlpha]",
		extractAll    : "Extract all files, sets the -a flag used by some modules",
		start         : "Start processing with deark at a specific byte offset",
		file2         : "An extra file that can be used by deark module to get the correct palette or image names"
	};
	bruteFlags   = { archive : {}, executable : {}, document : {}, font : { charOutType : "image" }, video : {} };
	checkForDups = true;

	bin    = "deark";
	outExt = ".png";
	args   = r =>
	{
		const a = ["-maxfiles", "9999"];
		if(r.flags.module)
			a.push("-m", r.flags.module);
		if(r.flags.start)
			a.push("-start", r.flags.start);
		if(r.flags.noThumbs)
			a.push("-main");
		if(r.flags.file2)
			a.push("-file2", r.flags.file2);
		if(r.flags.recombine)
			a.push("-d");
		if(r.flags.extractAll)
			a.push("-a");
		
		const opts = Array.force(r.flags.opt || []);
		if(r.flags.charOutType)
			opts.push(`char:output=${r.flags.charOutType || "image"}`);

		return [...a, ...opts.flatMap(opt => (["-opt", opt])), "-od", r.outDir(), "-o", "out", r.inFile()];
	};

	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});

		// fail fast if we have more than 1 output file, if we were told to
		if(r.flags.onlyIfOne)
		{
			const fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
			if(fileOutputPaths?.length>1)
			{
				await fileOutputPaths.parallelMap(async fileOutputPath => await fileUtil.unlink(fileOutputPath));
				return;
			}
		}

		// deark doesn't correctly decode Mac Japan encoded filenames
		if(r.flags.mac && RUNTIME.globalFlags?.osHint?.macintoshjp)
		{
			const decodeOpts = {processors : encodeUtil.macintoshProcessors.romanUTF8, region : "japan"};
			const fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
			await fileOutputPaths.parallelMap(async fileOutputPath =>
			{
				const subPath = path.relative(outDirPath, fileOutputPath);
				const newSubPath = (await subPath.split("/").parallelMap(async v => await encodeUtil.decodeMacintosh({data : v, ...decodeOpts}))).join("/");
				if(subPath===newSubPath)
					return;
				
				// we have to mkdir and rename because some files like archive/sit/LOOPDELO.SIT have two different directories, one encoded one not encoded but when decoded they are equal
				await Deno.mkdir(path.join(outDirPath, path.dirname(newSubPath)), {recursive : true});
				await Deno.rename(path.join(outDirPath, subPath), path.join(outDirPath, newSubPath));
			});
		}

		// for some image formats for some images (like PICT Daniel sample) deark will output multiple image files that are actually 1 single image. See: https://github.com/jsummers/deark/issues/41
		// NOTE: This fails with some files such as: • Figure 5 Window in List Mode.pict
		// NOTE!!! THIS IS A HUGE HACK. An attempt at re-writing it was started below in chainPost but ran into more roadblocks. So meh, this works for now
		if(r.flags.recombine)
		{
			const fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
			const imgInfo = {parts : []};

			for(const line of r.stdout.split("\n"))
			{
				const rectInfo = (line.match(/srcRect:\s\((?<x>\d+),(?<y>\d+)\)-\((?<w>\d+),(?<h>\d+)\)$/) || {})?.groups;
				if(rectInfo)
				{
					["w", "h"].forEach(k => { imgInfo[k] = Math.max(+rectInfo[k], imgInfo[k] || 0); });
					["x", "y"].forEach(k => { imgInfo[k] = +rectInfo[k]; });
					continue;
				}

				const filenameInfo = (line.match(/^Writing\s(?<filename>.+)$/) || {})?.groups;
				if(filenameInfo)
				{
					imgInfo.parts.push({filename : filenameInfo.filename, x : imgInfo.x, y : imgInfo.y});
					delete imgInfo.x;
					delete imgInfo.y;
					continue;		// eslint-disable-line sonarjs/no-redundant-jump
				}
			}

			// if we have a width and height and more than 1 part and none of those parts have the same x/y coordinate (PICT_2021.pict) then we can recombine them
			if(imgInfo.w && imgInfo.h && imgInfo.parts.length>1 && imgInfo.parts.length===imgInfo.parts.map(({x, y}) => `${x}x${y}`).unique().length)
			{
				r.xlog.debug`${imgInfo}`;
				const combinedFilePath = await fileUtil.genTempPath(undefined, ".png");
				await runUtil.run("magick", ["-size", `${imgInfo.w}x${imgInfo.h}`, "canvas:transparent", `PNG32:${combinedFilePath}`]);
				for(const part of imgInfo.parts)
				{
					const srcFilePath = fileOutputPaths.find(fileOutputPath => fileOutputPath.endsWith(path.basename(part.filename)));
					if(!srcFilePath)
					{
						r.xlog.warn`Unable to find deark sub image part ${part.filename} from possibles: [${fileOutputPaths.join("] [")}]`;
					}
					else
					{
						await runUtil.run("composite", ["-gravity", "NorthWest", "-geometry", `+${part.x}+${part.y}`, srcFilePath, combinedFilePath, combinedFilePath]);
						await fileUtil.unlink(srcFilePath);
					}
				}

				await runUtil.run("magick", [combinedFilePath, "-trim", "+repage", ...CONVERT_PNG_ARGS, path.join(outDirPath, `${r.originalInput.name}.png`)]);
			}
		}

		// so bsave images are very common, unfortunately there isn't a good way to determine what format that image is, so dexvert tries them all
		// this produces a bunch of junk images. the classify garbage tensor check catches some of them, but here we will try and remove some other junk
		if(r.flags.module==="bsave")
		{
			await (await fileUtil.tree(outDirPath, {nodir : true})).parallelMap(async fileOutputPath =>
			{
				const imgInfo = await imageUtil.getInfo(fileOutputPath);
				// this was mostly used back in the BASIC/DOS/Win95 days, so it's highly unlikely any image should be larger than 1600x1600
				if(imgInfo.width>1600 || imgInfo.height>1600)
					await fileUtil.unlink(fileOutputPath);
			});
		}

		// now we may be left with certain image formats like .bmp, .pict, .tiff, etc.
		// we used to wait until the end of the program and chained these to dexvert, but this took FOREVER
		// the reason we chained is because some of these formats are not supported by imagemagick, so the full dexvert converter chain is needed
		// but the vast majority will quickly convert with the first program each format is handled by
		// so for 'some' formats we will do a quick conversion here, and then any we don't do or that don't work, the chain check at the end will take care of
		// this introduces a 'slight' risk that some conversions that maybe fail but still prodce like a black image will be missed, but it's WAY worth it for the speed gain
		await quickConvertImages(r, await fileUtil.tree(outDirPath, {nodir : true}));
	};

	// deark output names are an MINOR NIGHTMARE
	// often they are just out.###.png (like image/amosIcons/)
	// however sometimes it contains additional data like internal filenames like out.###.something.png (like image/glowIcon and image/icns)
	// another example is image/macPaint/test.mac becoming out.000.Christie Brinkley.png which we want to turn into Christie Brinkley.png
	// however it doesn't even always have an extension and can just be out.000.manifest
	// or with archive/msa you get out.000.A where in this case A is either the filename or the extension, hard to say
	// it's different per format, which makes it pretty challenging to rename nice at a program level, but this does pretty good
	// If I change anything, test with: image/macPaint  image/amosIcons  image/glowIcon  image/icns  archive/msa  image/wpg  image/shg
	renameOut = {
		alwaysRename : true,
		regex        : /^out\.(?<num>\d{3,4})\.(?<rest>.+)$/,
		renamer      :
		[
			({suffix, newName}, {rest}) => restRenamer(rest, suffix, newName),
			({suffix}, {num, rest}) => [num, ".", ...restRenamer(rest, suffix)],
			({suffix, newName}, {num, rest}) => [num, ".", ...restRenamer(rest, suffix, newName)],
			({suffix}, {num, rest}) => [num, restRenamer(rest, suffix)]
		]
	};

	verify = (r, dexFile) =>
	{
		// These modules are a little loosey goosey with it's magic, so we have to check the output to make sure it's valid
		if(Object.entries({
			tinystuff : "Warning: Expected file size to be",
			zsq       : "Checksum error. Decompression probably failed"
		}).some(([module, message]) => r.stdout.includes(`Module: ${module}`) && r.stdout.includes(message)))
			return false;

		// Deark's newprintshop module can convert almost any file into a bunch of garbage. So if that was used with anything other than a .pog, nothing from it is worth keeping
		if(r.stdout.includes("Module: newprintshop") && r.f.input.ext.toLowerCase()!==".pog")
			return false;

		// DMG files incorrectly identified as ZLIB when sent to deark produces invalid 512byte output files, so check that here and deny them
		if(r.stdout.includes("zlib") && dexFile.ext===".unc" && dexFile.size===512)
			return false;

		// If a file extracts to > 3x it's original size, it's unlikely to be correct (http://dev.discmaster.textfiles.com/view/224/Deathmatch%20Arsenal%20V1.0%20(Arsenal%20Computer).ISO/wads_003/hunt.zip/HUNT.WAD/THINGS)
		if(r.stdout.includes("zlib") && dexFile.size>=(r.f.input.size*3))
			return false;

		return true;
	};

	// image/icns/abydos.icns produces 5 output files, 3 PNG and 2 JP2 (JPEG200)
	chain = "?resource_dasm -> ?dexvert";
	chainCheck = (r, chainFile, programid) =>
	{
		// very hacky, but certain files are known to be troublesome for one reason or another, so just skip them
		if(BAD_FILENAMES_TO_SKIP_CHAINING.includes(r.originalInput?.base?.toLowerCase()))
			return false;

		if(programid==="resource_dasm")
			return chainFile.ext.toLowerCase()===".rsrc";

		const chainFormat =
		{
			".bmp"  : "bmp",
			".eps"  : "eps",
			".jp2"  : "jpeg2000",
			".pict" : "pict",
			".qtif" : "qtif",
			".tif"  : "tiff",
			".tiff" : "tiff"
		}[chainFile.ext.toLowerCase()];

		return (chainFormat ? {asFormat : `image/${chainFormat}`} : false);
	};
	chainFailKeep = (r, chainInputFiles, chainResult, programid) => programid==="dexvert";
}
