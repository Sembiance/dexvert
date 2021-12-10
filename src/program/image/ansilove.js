import {Program} from "../../Program.js";

export class ansilove extends Program
{
	website = "https://www.ansilove.org/";
	package = "media-gfx/ansilove";
	unsafe  = true;
	flags   = {
		format : "Which ansilove format to use. Default: Let ansilove decide"
	};
	bin       = "ansilove";
	args      = async r => [...(r.flags.format ? ["-t", r.flags.format] : []), "-S", "-i", "-o", await r.outFile("out.png"), r.inFile()];
	renameOut = true;
}
