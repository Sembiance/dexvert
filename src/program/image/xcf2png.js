import {Program} from "../../Program.js";

export class xcf2png extends Program
{
	website       = "http://henning.makholm.net/software";
	gentooPackage = "media-gfx/xcftools";
	gentooOverlay = "dexvert";
	bin           = "xcf2png";
	args          = async r => ["-o", await r.outFile("out.png"), r.inFile()];
}
