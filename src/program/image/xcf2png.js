import {Program} from "../../Program.js";

export class xcf2png extends Program
{
	website = "http://henning.makholm.net/software";
	package = "media-gfx/xcftools";
	bin     = "xcf2png";
	args    = async r => ["-o", await r.outFile("out.png"), r.inFile()];
}
