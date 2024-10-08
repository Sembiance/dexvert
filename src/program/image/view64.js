import {Program} from "../../Program.js";

export class view64 extends Program
{
	website    = "http://view64.sourceforge.net/";
	package    = "media-gfx/view64";
	unsafe     = true;
	bin        = "view64pnm";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.pnm")});
	renameOut  = true;
	chain      = "convert";
}
