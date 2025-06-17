import {xu} from "xu";
import {Program} from "../../Program.js";

export class aolart2ppm2007 extends Program
{
	website   = "https://github.com/Sembiance/dexvert/base/dexvert/aolart2ppm/";
	loc       = "wine";
	bin       = "c:\\dexvert\\aolart2ppm2007\\AOL_ART.exe";
	args      = async r => [r.inFile(), await r.outFile("out.ppm")];
	wineData  = {
		timeout : xu.MINUTE
	};
	renameOut = true;
	chain     = "dexvert[asFormat:image/ppm]";
}
