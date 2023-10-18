import {Program} from "../../Program.js";

export class ybmtopbm extends Program
{
	website    = "http://netpbm.sourceforge.net/";
	package    = "media-libs/netpbm";
	bin        = "ybmtopbm";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.pbm")});
	renameOut  = true;
	chain      = "convert";
}
