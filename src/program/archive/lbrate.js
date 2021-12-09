import {Program} from "../../Program.js";

export class lbrate extends Program
{
	website   = "http://www.svgalib.org/rus/lbrate.html";
	package   = "app-arch/lbrate";
	bin       = "lbrate";
	args      = r => [r.inFile()];
	cwd       = r => r.outDir();
	renameOut = false;
}
