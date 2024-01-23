import {Program} from "../../Program.js";

export class recoil2png extends Program
{
	website    = "http://recoil.sourceforge.net";
	package    = "media-gfx/recoil";
	bruteFlags = { font : {} };
	bin        = "recoil2png";	// can use website tool to help identify 'what' a file is: https://recoil.sourceforge.net/web.html
	classify   = true;
	outExt     = ".png";
	args       = async r => ["-o", await r.outFile("out.png"), r.inFile()];
	renameOut  = true;
}
