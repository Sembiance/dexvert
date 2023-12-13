import {Program} from "../../Program.js";

export class aolart2ppm2015 extends Program
{
	website   = "https://github.com/Sembiance/dexvert/base/dexvert/aolart2ppm/";
	loc       = "wine";
	bin       = "c:\\dexvert\\aolart2ppm2015\\AOL_ART.exe";
	args      = async r => [r.inFile(), await r.outFile("out.ppm")];
	renameOut = true;
	chain     = "dexvert[asFormat:image/ppm]";
}
