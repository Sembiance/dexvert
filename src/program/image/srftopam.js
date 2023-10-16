import {Program} from "../../Program.js";

export class srftopam extends Program
{
	website    = "http://netpbm.sourceforge.net/";
	package    = "media-libs/netpbm";
	bin        = "srftopam";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.pam")});
	renameOut  = true;
	chain      = "convert";
}
