import {Program} from "../../Program.js";

export class sldtoppm extends Program
{
	website    = "http://netpbm.sourceforge.net/";
	package    = "media-libs/netpbm";
	bin        = "sldtoppm";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.ppm")});
	chain      = "convert";
}
