import {xu} from "xu";
import {Program} from "../../Program.js";

export class iff_convert extends Program
{
	website = "http://www.boomerangsworld.de/cms/tools/iff-convert.html";
	package = "app-arch/iff-convert";
	flags   = {
		framesOnly  : "Set to true to only allow frames output, no .txt files or masks",
		keepAll     : "Set to true to keep all files. Normally mask files are discarded.",
		outType     : "Which type to convert to. For list run `iff-convert --help` Default: binary"
	};
	bin              = "iff-convert";
	filenameEncoding = "iso-8859-1";	// AmigaOS uses this: http://lclevy.free.fr/adflib/adf_info.html#p54
	args             = r => [`--output-dir=${r.outDir()}`, `--format=${r.flags.outType || "binary"}`, r.inFile()];
	renameOut        = {
		alwaysRename : true,
		regex        : /iff_dump-?(?<rest>.+)$/,
		renamer      :
		[
			(ignored, {rest}) => [rest]
		]
	};

	verify = (r, dexFile) =>
	{
		if(r.flags.keepAll)
			return true;

		if(r.flags.framesOnly)
			return dexFile.ext.toLowerCase()===".ppm";
		
		return dexFile.ext.toLowerCase()!==".pgm";	// delete mask files
	};
	chain      = "?convert";
	chainCheck = (r, chainFile) => [".pgm", ".ppm"].includes(chainFile.ext.toLowerCase());
}
