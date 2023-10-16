import {Program} from "../../Program.js";

export class mrftopbm extends Program
{
	website    = "http://netpbm.sourceforge.net/";
	package    = "media-libs/netpbm";
	bin        = "mrftopbm";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.pbm")});
	renameOut  = true;
	chain      = "convert";
}
