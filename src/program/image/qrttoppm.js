import {Program} from "../../Program.js";

export class qrttoppm extends Program
{
	website    = "http://netpbm.sourceforge.net/";
	package    = "media-libs/netpbm";
	bin        = "qrttoppm";
	unsafe     = true;
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.ppm")});
	renameOut  = true;
	chain      = "convert";
}
