import {Program} from "../../Program.js";

export class recoil2png extends Program
{
	website = "http://recoil.sourceforge.net";
	package = "media-gfx/recoil";
	flags   = {
		format : "Specify which format to convert as. Default: let recoil decide"
	};
	bruteFlags = { font : {} };
	classify   = true;
	bin        = "recoil2png";	// can use website tool to help identify 'what' a file is: https://recoil.sourceforge.net/web.html
	outExt     = ".png";
	args       = async r => [...(r.flags.format ? [`--format=${r.flags.format}`] : []), "-o", await r.outFile("out.png"), r.inFile()];
	renameOut  = true;
}
