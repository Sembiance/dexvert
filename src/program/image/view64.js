import {Program} from "../../Program.js";

export class view64 extends Program
{
	website       = "http://view64.sourceforge.net/";
	gentooPackage = "media-gfx/view64";
	gentooOverlay = "dexvert";
	unsafe        = true;
	bin           = "view64pnm";
	args          = r => [r.inFile()];
	runOptions    = async r => ({stdoutFilePath : await r.outFile("out.pnm")});
	chain         = "convert"
}
