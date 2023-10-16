import {Program} from "../../Program.js";

export class lispmtopgm extends Program
{
	website    = "http://netpbm.sourceforge.net/";
	package    = "media-libs/netpbm";
	bin        = "lispmtopgm";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.pgm")});
	renameOut  = true;
	chain      = "convert";
}
