import {xu} from "xu";
import {Program} from "../../Program.js";

export class nconvert extends Program
{
	website = "https://www.xnview.com/en/nconvert/";
	package = "media-gfx/nconvert";
	flags   = {
		format     : "Which nconvert format to use for conversion. For list run `nconvert -help` Default: Let nconvert decide",
		extractAll : "Convert all files within, instead of just 1"
	};

	bin       = "nconvert";
	outExt    = ".png";
	args      = async r => [...(r.flags.extractAll ? ["-xall"] : []), ...(r.flags.format ? ["-in", r.flags.format] : []), "-out", "png", "-o", await r.outFile("out.png"), r.inFile()];
	renameOut = {
		alwaysRename : true,
		regex        : /^out-(?<num>\d+)(?<ext>\.[^.]+)$/,	// this regex assumes the input filename doesn't have an underscore
		renamer      :
		[
			({numFiles}, {num, ext}) => [num.padStart(numFiles.toString().length, "0"), ext],
			({newName, newExt}) => [newName, newExt]
		]
	};
}
