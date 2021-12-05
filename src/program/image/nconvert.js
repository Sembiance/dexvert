import {xu} from "xu";
import {Program} from "../../Program.js";

export class nconvert extends Program
{
	website = "https://www.xnview.com/en/nconvert/";
	package = "media-gfx/nconvert";
	flags   = {
		format : "Which nconvert format to use for conversion. For list run `nconvert -help` Default: Let nconvert decide"
	};

	bin    = "nconvert";
	outExt = ".png";
	args   = async r => [...(r.flags.format ? ["-in", r.flags.format] : []), "-out", "png", "-o", await r.outFile("out.png"), r.inFile()];
}
