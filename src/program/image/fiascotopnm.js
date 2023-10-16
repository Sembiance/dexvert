import {Program} from "../../Program.js";

export class fiascotopnm extends Program
{
	website    = "http://netpbm.sourceforge.net/";
	package    = "media-libs/netpbm";
	bin        = "fiascotopnm";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.pnm")});
	renameOut  = true;
	chain      = "convert";
}
