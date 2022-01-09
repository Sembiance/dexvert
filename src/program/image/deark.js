import {Program} from "../../Program.js";

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
		"module"      : "Which deark module to forcibly set. For list run `deark -modules` Default: Let deark decide",
		"charOutType" : "Which type of output to use when converting character based files. Can be \"image\" or \"html\" Default: Let deark decide.",
		"opt"         : "An array of additional -opt <option> arguments to pass to deark. For list see: https://github.com/jsummers/deark",
		"noThumbs"    : "Don't extract any thumb files found",
		"file2"       : "An extra file that can be used by deark module to get the correct palette or image names"
	};

	bin    = "deark";
	outExt = ".png";
	args   = r =>
	{
		const a = ["-maxfiles", "9999"];
		if(r.flags.module)
			a.push("-m", r.flags.module);
		if(r.flags.noThumbs)
			a.push("-main");
		if(r.flags.file2)
			a.push("-file2", r.flags.file2);
		
		const opts = Array.force(r.flags.opt || []);
		if(r.flags.charOutType)
			opts.push(`char:output=${r.flags.charOutType || "image"}`);
		
		return [...a, ...opts.flatMap(opt => (["-opt", opt])), "-od", r.outDir(), "-o", "out", r.inFile()];
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

	verify = r =>
	{
		// Deark's newprintshop module can convert almost any file into a bunch of garbage. So if that was used with anything other than a .pog, nothing from it is worth keeping
		if(r.stdout.includes("Module: newprintshop") && r.f.input.ext.toLowerCase()!==".pog")
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
