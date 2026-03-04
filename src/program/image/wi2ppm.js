import {Program} from "../../Program.js";

export class wi2ppm extends Program
{
	loc       = "wine";
	bin       = "c:\\dexvert\\wi2ppm\\wi2ppm.exe";
	args      = async r => [r.inFile(), await r.outFile("out.ppm")];
	renameOut = true;
	chain     = "convert";
}
