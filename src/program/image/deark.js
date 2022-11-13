import {xu} from "xu";
import {Program, RUNTIME} from "../../Program.js";
import {encodeUtil, fileUtil} from "xutil";
import {path} from "std";

function restRenamer(rest, suffix, newName)
{
	// if we don't have a period in our rest, then if it's a common extension fall back on our newName
	if(!rest.includes("."))
		return ["gif", "png", "ico", "jpg", "bmp", "eps", "svg", "jp2", "qtif", "tif", "tiff", "bin", "ptr", "icns", "wmf"].includes(rest) && newName ? [newName, suffix, ".", rest] : [suffix, rest];
	
	const restParts = rest.split(".");
	return [restParts.slice(0, -1).join("."), suffix, ".", restParts.at(-1)];
}

export class deark extends Program
{
	website = "https://entropymine.com/deark/";
	package = "app-arch/deark";
	flags   = {
		"mac"         : "Set this flag to treat the files extracted as mac files and rename them",
		"module"      : "Which deark module to forcibly set. For list run `deark -modules` Default: Let deark decide",
		"charOutType" : "Which type of output to use when converting character based files. Can be \"image\" or \"html\" Default: Let deark decide.",
		"opt"         : "An array of additional -opt <option> arguments to pass to deark. For list see: https://github.com/jsummers/deark",
		"noThumbs"    : "Don't extract any thumb files found",
		"start"       : "Start processing with deark at a specific byte offset",
		"file2"       : "An extra file that can be used by deark module to get the correct palette or image names"
	};
	bruteFlags = { archive : {}, executable : {}, document : {}, font : { charOutType : "image" }, video : {} };

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
		
		const opts = Array.force(r.flags.opt || []);
		if(r.flags.charOutType)
			opts.push(`char:output=${r.flags.charOutType || "image"}`);
		
		return [...a, ...opts.flatMap(opt => (["-opt", opt])), "-od", r.outDir(), "-o", "out", r.inFile()];
	};

	postExec = async r =>
	{
		// only need to do this if we are macintoshjp region, otherwise deark correctly converts filenames to roman
		if(!r.flags.mac || !RUNTIME.globalFlags?.osHint?.macintoshjp)
			return;

		const decodeOpts = {processors : encodeUtil.macintoshProcessors.romanUTF8, region : "japan"};
		const outDirPath = r.outDir({absolute : true});
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
	chain = "?dexvert";
	chainCheck = (r, chainFile) =>
	{
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
}
