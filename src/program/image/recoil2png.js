import {Program} from "../../Program.js";

export class recoil2png extends Program
{
	website       = "http://recoil.sourceforge.net";
	gentooPackage = "media-gfx/recoil";
	gentooOverlay = "dexvert";
	bin           = "recoil2png";
	outExt        = ".png";
	args          = async r => ["-o", await r.outFile("out.png"), r.inFile()]
}
